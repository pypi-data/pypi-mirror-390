from enum import Enum


class CategorySeasonalAndHolidayCategory(str, Enum):
    SEASONALANDHOLIDAY = "seasonalAndHoliday"

    def __str__(self) -> str:
        return str(self.value)
