from django.core.management.base import BaseCommand
from django.db import transaction
import json
from pathlib import Path
from finacc.models.accounts import Account
from finacc.models.company import Company


class Command(BaseCommand):
    help = "Bootstrap Chart of Accounts for a company"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)
    parser.add_argument("--template", default="india_basic")


@transaction.atomic
def handle(self, *args, **opts):
    company = Company.objects.get(id=opts["company"])
    data = json.loads((Path(__file__).resolve().parents[3] / "data" / f"coa_{opts['template']}.json").read_text())
    created = 0
    for row in data:
        Account.objects.update_or_create(
        company=company, code=row["code"],
        defaults={
            "name": row["name"],
            "kind": row["kind"],
            "normal_balance": row["normal_balance"],
            "is_leaf": row.get("is_leaf", True),
            "is_active": True,
            },
        )
    created += 1
    self.stdout.write(self.style.SUCCESS(f"Loaded {created} accounts for {company.name}"))