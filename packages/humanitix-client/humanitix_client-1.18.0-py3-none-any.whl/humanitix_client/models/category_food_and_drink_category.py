from enum import Enum


class CategoryFoodAndDrinkCategory(str, Enum):
    FOODANDDRINK = "foodAndDrink"

    def __str__(self) -> str:
        return str(self.value)
