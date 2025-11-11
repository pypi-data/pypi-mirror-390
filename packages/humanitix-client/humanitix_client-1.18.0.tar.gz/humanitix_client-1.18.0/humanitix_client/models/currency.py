from enum import Enum


class Currency(str, Enum):
    AUD = "AUD"
    CAD = "CAD"
    FJD = "FJD"
    NZD = "NZD"
    USD = "USD"

    def __str__(self) -> str:
        return str(self.value)
