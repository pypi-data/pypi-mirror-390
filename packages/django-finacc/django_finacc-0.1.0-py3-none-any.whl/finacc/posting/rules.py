from decimal import Decimal
from finacc.models.journal import JournalEntry, JournalLine




def create_simple_entry(company, date, currency, memo, lines):
    """lines = list of dict(account, debit, credit, description?)"""
    je = JournalEntry.objects.create(company=company, date=date, currency=currency, memo=memo)
    for l in lines:
        JournalLine.objects.create(entry=je, **l)
    return je