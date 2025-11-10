from django.conf import settings
from inventory.conf import get as confget


# Auto-hook into django-sales signals for product lines
try:
    from sales.posting.signals import invoice_posted # emitted in your sales package
    from sales.models.doc_invoice import SalesInvoice
    from sales.models.item import Item as SalesItem
    from inventory.models.item import StockItem
    from inventory.models.move import StockMove
    from inventory.enums import MoveType
    from inventory.posting.adapters import issue_stock


    def _on_invoice_posted(sender, **kwargs):
        inv = kwargs.get("invoice")
        if not confget("AUTO_HOOK_SALES"):
            return
        for line in inv.lines.select_related("item").all():
            if getattr(line.item, "type", "product") != "product":
                continue
            try:
                si = StockItem.objects.get(company=inv.company, sku=line.item.sku)
            except StockItem.DoesNotExist:
                continue # not inventory-managed
            move = StockMove.objects.create(company=inv.company, item=si, warehouse=inv.company.warehouse_set.first(), date=inv.date, currency=inv.currency, type=MoveType.OUT.value, qty=line.qty, unit_cost=0, ref=inv.number)
            issue_stock(move)


            invoice_posted.connect(_on_invoice_posted)
except Exception:
    pass