from django.db import models


class AuditLog(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    action = models.CharField(max_length=64)
    ref = models.CharField(max_length=64)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)