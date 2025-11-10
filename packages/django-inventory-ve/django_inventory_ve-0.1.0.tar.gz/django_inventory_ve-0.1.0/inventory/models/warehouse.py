from django.db import models


class Warehouse(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ("company", "code")


    def __str__(self):
        return f"{self.code} — {self.name}"