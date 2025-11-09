from decimal import Decimal


def nz(value):
    return value or Decimal("0")