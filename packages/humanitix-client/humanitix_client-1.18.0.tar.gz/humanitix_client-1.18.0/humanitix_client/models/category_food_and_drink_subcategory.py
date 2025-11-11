from enum import Enum


class CategoryFoodAndDrinkSubcategory(str, Enum):
    BEER = "beer"
    FOOD = "food"
    OTHER = "other"
    SPIRITS = "spirits"
    WINE = "wine"

    def __str__(self) -> str:
        return str(self.value)
