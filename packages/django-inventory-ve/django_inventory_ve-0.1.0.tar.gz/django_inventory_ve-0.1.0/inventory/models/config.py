from django.db import models


class InventoryAccountMapping(models.Model):
    company = models.OneToOneField("finacc.Company", on_delete=models.CASCADE)
    inventory_asset = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="inv_asset")
    cogs = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="inv_cogs")
    inventory_adjustment = models.ForeignKey("finacc.Account", on_delete=models.PROTECT, related_name="inv_adjust", null=True, blank=True)