from enum import Enum


class CategoryHomeAndLifestyleCategory(str, Enum):
    HOMEANDLIFESTYLE = "homeAndLifestyle"

    def __str__(self) -> str:
        return str(self.value)
