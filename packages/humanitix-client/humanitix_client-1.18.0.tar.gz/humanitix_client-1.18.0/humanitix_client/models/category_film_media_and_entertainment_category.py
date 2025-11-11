from enum import Enum


class CategoryFilmMediaAndEntertainmentCategory(str, Enum):
    FILMMEDIAANDENTERTAINMENT = "filmMediaAndEntertainment"

    def __str__(self) -> str:
        return str(self.value)
