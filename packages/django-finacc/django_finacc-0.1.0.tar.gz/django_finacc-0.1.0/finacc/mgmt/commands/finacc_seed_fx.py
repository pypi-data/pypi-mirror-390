from django.core.management.base import BaseCommand
from datetime import timedelta, date
from decimal import Decimal
from finacc.models.company import Company, FxRate


class Command(BaseCommand):
    help = "Seed flat FX rate for a date range (dev/testing)"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)
    parser.add_argument("--base", type=str, required=True)
    parser.add_argument("--quote", type=str, required=True)
    parser.add_argument("--from", dest="date_from", type=str, required=True)
    parser.add_argument("--to", dest="date_to", type=str, required=True)
    parser.add_argument("--rate", type=str, required=True)


def handle(self, *args, **opts):
    c = Company.objects.get(id=opts["company"])
    d0 = date.fromisoformat(opts["date_from"])
    d1 = date.fromisoformat(opts["date_to"])
    rate = Decimal(opts["rate"])
    n = 0
    d = d0
    while d <= d1:
        FxRate.objects.update_or_create(company=c, date=d, base=opts["base"], quote=opts["quote"], defaults={"rate": rate})
        d += timedelta(days=1)
        n += 1
    self.stdout.write(self.style.SUCCESS(f"Seeded {n} FX rows"))