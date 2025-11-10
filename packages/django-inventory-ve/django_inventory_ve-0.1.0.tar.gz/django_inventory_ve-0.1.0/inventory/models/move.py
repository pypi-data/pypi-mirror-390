from django.db import models
from inventory.enums import MoveType


class StockMove(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    item = models.ForeignKey("inventory.StockItem", on_delete=models.PROTECT)
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.PROTECT)
    date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    type = models.CharField(max_length=16, choices=[(m.value, m.value) for m in MoveType])
    qty = models.DecimalField(max_digits=18, decimal_places=6)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0) # cost per unit for IN
    ref = models.CharField(max_length=64, blank=True) # link to invoice/bill number
    memo = models.CharField(max_length=255, blank=True)
    posted_entry_id = models.IntegerField(null=True, blank=True)