from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from finacc.exceptions import PostingError, PeriodLockedError
from finacc.models.period import PeriodLock
from finacc.utils.fx import convert_to_base
from finacc.validators import nz




def _check_locked(company, date):
    lock = PeriodLock.objects.filter(company=company).order_by("-through_date").first()
    if lock and date <= lock.through_date:
        raise PeriodLockedError(f"Period locked through {lock.through_date}")




def validate_balanced(entry):
    dr = sum((l.debit for l in entry.lines.all()), start=Decimal("0"))
    cr = sum((l.credit for l in entry.lines.all()), start=Decimal("0"))
    if dr != cr:
        raise PostingError(f"Unbalanced entry: DR {dr} != CR {cr}")




def fill_base_amounts(entry):
    for line in entry.lines.all():
        gross = nz(line.debit) - nz(line.credit)
        line.amount_base = convert_to_base(entry.company, entry.currency, entry.date, gross)
        line.save(update_fields=["amount_base"])




@transaction.atomic
def post_entry(entry):
    _check_locked(entry.company, entry.date)
    validate_balanced(entry)
    fill_base_amounts(entry)
    entry.is_posted = True
    entry.posted_at = timezone.now()
    entry.save(update_fields=["is_posted", "posted_at"])
    return entry