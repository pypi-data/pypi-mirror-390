from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class PostingSource(models.Model):
    app_label = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    object_id = models.CharField(max_length=64)
    external_ref = models.CharField(max_length=128, blank=True)


class JournalEntry(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE, related_name="journal_entries")
    date = models.DateField()
    memo = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3)
    source = models.ForeignKey(PostingSource, null=True, blank=True, on_delete=models.SET_NULL)
    is_posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class JournalLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey("finacc.Account", on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(0)])
    amount_base = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))