from enum import Enum


class CategoryCharityAndCausesCategory(str, Enum):
    CHARITYANDCAUSES = "charityAndCauses"

    def __str__(self) -> str:
        return str(self.value)
