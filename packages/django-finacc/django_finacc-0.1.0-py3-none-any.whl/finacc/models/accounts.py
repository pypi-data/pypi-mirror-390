from django.db import models
from finacc.enums import AccountKind, NormalBalance


class Account(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE, related_name="accounts")
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    kind = models.CharField(max_length=16, choices=[(k.value, k.value) for k in AccountKind])
    normal_balance = models.CharField(max_length=6, choices=[(n.value, n.value) for n in NormalBalance])
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    is_leaf = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)


class Meta:
    unique_together = ("company", "code")


def __str__(self):
    return f"{self.code} — {self.name}"