from django.db import models


class FiscalYear(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    label = models.CharField(max_length=32)


class Period(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    code = models.CharField(max_length=16)
    is_closed = models.BooleanField(default=False)


class Meta:
    unique_together = ("company", "code")


class PeriodLock(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    through_date = models.DateField()