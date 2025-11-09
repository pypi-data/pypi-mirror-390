from django.db import models


class Tax(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    is_price_inclusive = models.BooleanField(default=False)


class Meta:
    unique_together = ("company", "code")


class TaxRate(models.Model):
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name="rates")
    effective_from = models.DateField()
    percent = models.DecimalField(max_digits=7, decimal_places=4)


class Meta:
    unique_together = ("tax", "effective_from")


class TaxSplit(models.Model):
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, related_name="splits")
    component = models.CharField(max_length=16) # CGST/SGST/IGST
    share_percent = models.DecimalField(max_digits=7, decimal_places=4)