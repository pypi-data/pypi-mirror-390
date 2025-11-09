from enum import Enum


class AccountKind(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"