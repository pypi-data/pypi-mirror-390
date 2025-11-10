from decimal import Decimal
from inventory.utils.money import q2
# Weighted average: new_avg = (qty_old*avg_old + qty_in*price_in) / (qty_old + qty_in)
def weighted_avg(qty_old: Decimal, avg_old: Decimal, qty_in: Decimal, price_in: Decimal) -> Decimal:
    total_cost = (qty_old * avg_old) + (qty_in * price_in)
    total_qty = qty_old + qty_in
    if total_qty == 0:
        return q2(Decimal("0"))
    return q2(total_cost / total_qty)