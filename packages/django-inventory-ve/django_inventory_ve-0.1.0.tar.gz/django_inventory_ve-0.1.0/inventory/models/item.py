from django.db import models


class StockItem(models.Model):
    """Inventory-managed item (product only). Match by SKU with sales/purchase items."""
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    uom = models.CharField(max_length=16, default="pcs")
    cost_method = models.CharField(max_length=8, default="avg") # avg|fifo
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ("company", "sku")


class StockQuant(models.Model):
    item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="quants")
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    avg_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0) # for AVG


    class Meta:
        unique_together = ("item", "warehouse")