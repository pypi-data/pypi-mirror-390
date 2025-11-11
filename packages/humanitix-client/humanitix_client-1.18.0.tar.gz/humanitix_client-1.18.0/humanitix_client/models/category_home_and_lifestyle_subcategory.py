from enum import Enum


class CategoryHomeAndLifestyleSubcategory(str, Enum):
    DATING = "dating"
    HOMEANDGARDEN = "homeAndGarden"
    OTHER = "other"
    PETSANDANIMALS = "petsAndAnimals"

    def __str__(self) -> str:
        return str(self.value)
