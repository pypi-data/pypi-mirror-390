from enum import Enum


class CategoryGovernmentAndPoliticsCategory(str, Enum):
    GOVERNMENTANDPOLITICS = "governmentAndPolitics"

    def __str__(self) -> str:
        return str(self.value)
