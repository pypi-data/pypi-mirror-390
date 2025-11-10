from decimal import Decimal
from finacc.posting.rules import create_simple_entry
from finacc.posting.engine import post_entry
from inventory.models.move import StockMove
from inventory.models.valuation import StockValuationLayer
from inventory.models.item import StockQuant
from inventory.models.config import InventoryAccountMapping
from inventory.utils.costing import weighted_avg
from inventory.utils.money import q2




def _get_quant(item, warehouse):
    from inventory.models.item import StockQuant
    quant, _ = StockQuant.objects.get_or_create(item=item, warehouse=warehouse, defaults={"qty": 0, "avg_cost": 0})
    return quant




def receive_stock(move: StockMove):
    """Process an IN move: create valuation layer, update quant avg_cost/qty, post Asset debit."""
    mapping = InventoryAccountMapping.objects.get(company=move.company)
    quant = _get_quant(move.item, move.warehouse)
    # Update avg cost (weighted) and qty
    new_avg = weighted_avg(quant.qty, quant.avg_cost, move.qty, move.unit_cost)
    quant.avg_cost = new_avg
    quant.qty = quant.qty + move.qty
    quant.save(update_fields=["avg_cost", "qty"])


    # Valuation layer
    total = q2(move.qty * move.unit_cost)
    svl = StockValuationLayer.objects.create(item=move.item, warehouse=move.warehouse, date=move.date, qty=move.qty, unit_cost=move.unit_cost, total_cost=total, ref=move.ref)


    # Post to accounting: DR Inventory Asset, CR Inventory Adjustment (or GRNI if you prefer later)
    lines = [
    {"account": mapping.inventory_asset, "debit": total, "credit": Decimal("0.00"), "description": f"INV IN {move.ref}"},
    ]
    if mapping.inventory_adjustment:
        lines.append({"account": mapping.inventory_adjustment, "credit": total, "debit": Decimal("0.00"), "description": "INV Adj"})
    else:
        # if no adjustment account configured, just create a zero-sum (no CR) and let purchase posting offset this (common in GRNI designs)
        pass


    je = create_simple_entry(move.company, move.date, move.currency, f"INV IN {move.ref}", lines)
    posted = post_entry(je)
    move.posted_entry_id = posted.id; move.save(update_fields=["posted_entry_id"])
    return posted




def issue_stock(move: StockMove):
    """Process an OUT move: consume at avg cost (or FIFO in future), create SVL, post COGS."""
    mapping = InventoryAccountMapping.objects.get(company=move.company)
    quant = _get_quant(move.item, move.warehouse)
    if move.qty > quant.qty:
        raise ValueError("Insufficient stock to issue")
    unit_cost = quant.avg_cost # for AVG method
    total = q2(move.qty * unit_cost)
    quant.qty = quant.qty - move.qty
    quant.save(update_fields=["qty"])


    svl = StockValuationLayer.objects.create(item=move.item, warehouse=move.warehouse, date=move.date, qty=-move.qty, unit_cost=unit_cost, total_cost=-total, ref=move.ref)


    # Post to accounting: DR COGS, CR Inventory Asset
    lines = [
    {"account": mapping.cogs, "debit": total, "credit": Decimal("0.00"), "description": f"COGS {move.ref}"},
    {"account": mapping.inventory_asset, "credit": total, "debit": Decimal("0.00"), "description": f"INV OUT {move.ref}"},
    ]
    je = create_simple_entry(move.company, move.date, move.currency, f"INV OUT {move.ref}", lines)
    posted = post_entry(je)
    move.posted_entry_id = posted.id; move.save(update_fields=["posted_entry_id"])
    return posted