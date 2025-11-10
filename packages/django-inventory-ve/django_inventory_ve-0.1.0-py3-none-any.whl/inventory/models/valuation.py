from django.db import models


class StockValuationLayer(models.Model):
    item = models.ForeignKey("inventory.StockItem", on_delete=models.CASCADE)
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.CASCADE)
    date = models.DateField()
    qty = models.DecimalField(max_digits=18, decimal_places=6) # +in / -out
    unit_cost = models.DecimalField(max_digits=18, decimal_places=2) # booked cost per unit
    total_cost = models.DecimalField(max_digits=18, decimal_places=2) # qty * unit_cost (sign matches qty)
    ref = models.CharField(max_length=64, blank=True)