from decimal import Decimal
from finacc.utils.money import quant4, quant2
from finacc.models.company import FxRate


def fx_rate(company, date, base: str, quote: str) -> Decimal:
    if base == quote:
        return Decimal("1")
    try:
        row = FxRate.objects.get(company=company, date=date, base=base, quote=quote)
        return quant4(row.rate)
    except FxRate.DoesNotExist:
        raise ValueError(f"Missing FX rate for {date} {base}/{quote}")


def convert(company, date, amount: Decimal, base: str, quote: str) -> Decimal:
    r = fx_rate(company, date, base, quote)
    return quant2(Decimal(amount) * r)


def convert_to_base(company, txn_currency: str, date, amount: Decimal) -> Decimal:
    base = company.base_currency
    return convert(company, date, amount, txn_currency, base)