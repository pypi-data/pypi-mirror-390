from enum import Enum


class OrderPaymentType(str, Enum):
    BANKDEPOSIT = "bankDeposit"
    CASH = "cash"
    COMPLIMENTARY = "complimentary"
    EFTPOS = "eftpos"
    NOPAYMENTNECESSARY = "noPaymentNecessary"
    OTHER = "other"
    PAYPAL = "payPal"
    VOUCHER = "voucher"

    def __str__(self) -> str:
        return str(self.value)
