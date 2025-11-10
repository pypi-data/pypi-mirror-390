from django.db import models
from fixedassets.enums import DepreciationMethod

class AssetCategory(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    depreciation_method = models.CharField(max_length=8, choices=[(m.value, m.value) for m in DepreciationMethod], default=DepreciationMethod.SLM.value)
    useful_life_years = models.IntegerField(default=5)
    residual_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    wdv_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # for WDV

    def __str__(self):
        return self.name


class Asset(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    purchase_date = models.DateField()
    currency = models.CharField(max_length=3, default="INR")
    cost = models.DecimalField(max_digits=18, decimal_places=2)
    accumulated_depr = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    book_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return f"{self.code} — {self.name}"
