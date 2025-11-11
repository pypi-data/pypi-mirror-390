from enum import Enum


class CategoryScienceAndTechnologyCategory(str, Enum):
    SCIENCEANDTECHNOLOGY = "scienceAndTechnology"

    def __str__(self) -> str:
        return str(self.value)
