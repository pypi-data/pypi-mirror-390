from enum import Enum


class CategoryTravelAndOutdoorCategory(str, Enum):
    TRAVELANDOUTDOOR = "travelAndOutdoor"

    def __str__(self) -> str:
        return str(self.value)
