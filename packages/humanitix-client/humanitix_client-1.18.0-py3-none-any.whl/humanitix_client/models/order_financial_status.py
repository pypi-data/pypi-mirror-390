from enum import Enum


class OrderFinancialStatus(str, Enum):
    FREE = "free"
    PAID = "paid"
    PARTIALLYREFUNDED = "partiallyRefunded"
    REFUNDED = "refunded"

    def __str__(self) -> str:
        return str(self.value)
