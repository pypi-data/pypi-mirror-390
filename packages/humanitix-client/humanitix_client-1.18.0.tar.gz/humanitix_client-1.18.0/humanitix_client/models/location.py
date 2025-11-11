from enum import Enum


class Location(str, Enum):
    AU = "AU"
    CA = "CA"
    DE = "DE"
    FJ = "FJ"
    GB = "GB"
    MX = "MX"
    MY = "MY"
    NZ = "NZ"
    SG = "SG"
    US = "US"

    def __str__(self) -> str:
        return str(self.value)
