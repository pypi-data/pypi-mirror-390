from django.db import models


class BaseDocument(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    number = models.CharField(max_length=32)
    date = models.DateField()
    currency = models.CharField(max_length=3)
    total = models.DecimalField(max_digits=18, decimal_places=2)


    class Meta:
        abstract = True