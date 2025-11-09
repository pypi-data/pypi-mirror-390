from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200)
    legal_name = models.CharField(max_length=255, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    base_currency = models.CharField(max_length=3, default="INR")
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name


class FxRate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="fx_rates")
    date = models.DateField()
    base = models.CharField(max_length=3)
    quote = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=8)


class Meta:
    unique_together = ("company", "date", "base", "quote")  