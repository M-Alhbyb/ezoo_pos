from enum import Enum


class LedgerTransactionType(str, Enum):
    SALE = "SALE"
    PAYMENT = "PAYMENT"
    RETURN = "RETURN"
