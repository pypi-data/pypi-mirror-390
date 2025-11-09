from django.core.management.base import BaseCommand
from django.db import transaction
from finacc.models.period import Period


class Command(BaseCommand):
    help = "Soft-close a period"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)
    parser.add_argument("--code", type=str, required=True)


@transaction.atomic
def handle(self, *args, **opts):
    p = Period.objects.get(company_id=opts["company"], code=opts["code"])
    p.is_closed = True
    p.save(update_fields=["is_closed"])
    self.stdout.write(self.style.SUCCESS(f"Closed period {p.code}"))