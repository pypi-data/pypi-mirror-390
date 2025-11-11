from enum import Enum


class CategoryHealthAndWellnessCategory(str, Enum):
    HEALTHANDWELLNESS = "healthAndWellness"

    def __str__(self) -> str:
        return str(self.value)
