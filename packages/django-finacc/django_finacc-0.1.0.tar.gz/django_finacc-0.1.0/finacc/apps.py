from django.apps import AppConfig


class FinaccConfig(AppConfig):
    name = "finacc"
    verbose_name = "Financial Accounting"


def ready(self):
    # Import signals to ensure handlers are registered
    from .posting import signals # noqa