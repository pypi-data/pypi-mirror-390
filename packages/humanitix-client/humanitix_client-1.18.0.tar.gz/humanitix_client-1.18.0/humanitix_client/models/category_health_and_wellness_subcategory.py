from enum import Enum


class CategoryHealthAndWellnessSubcategory(str, Enum):
    MEDICAL = "medical"
    MENTALHEALTH = "mentalHealth"
    OTHER = "other"
    PERSONALHEALTH = "personalHealth"
    SPA = "spa"
    YOGA = "yoga"

    def __str__(self) -> str:
        return str(self.value)
