from enum import Enum


class CategoryPerformingAndVisualArtsCategory(str, Enum):
    PERFORMINGANDVISUALARTS = "performingAndVisualArts"

    def __str__(self) -> str:
        return str(self.value)
