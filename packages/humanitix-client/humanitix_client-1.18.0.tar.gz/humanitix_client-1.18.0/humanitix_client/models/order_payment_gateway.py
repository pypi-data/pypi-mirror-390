from enum import Enum


class OrderPaymentGateway(str, Enum):
    AFTERPAY = "afterpay"
    BPOINT = "bpoint"
    BRAINTREE = "braintree"
    CASH = "cash"
    CREDIT = "credit"
    DISCOVER_NSW = "discover-nsw"
    GIFT_CARD = "gift-card"
    INVOICE = "invoice"
    MANUAL = "manual"
    PAYPAL = "paypal"
    PIN = "pin"
    STRIPE = "stripe"
    STRIPE_PAYMENTS = "stripe-payments"
    TILL = "till"
    TILLTERMINAL = "tillTerminal"
    WORLDPAY = "worldpay"
    ZIPMONEY = "zipmoney"

    def __str__(self) -> str:
        return str(self.value)
