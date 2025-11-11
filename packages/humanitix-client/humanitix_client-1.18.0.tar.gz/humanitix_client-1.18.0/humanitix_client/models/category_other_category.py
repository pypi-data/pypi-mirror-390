from enum import Enum


class CategoryOtherCategory(str, Enum):
    OTHER = "other"

    def __str__(self) -> str:
        return str(self.value)
