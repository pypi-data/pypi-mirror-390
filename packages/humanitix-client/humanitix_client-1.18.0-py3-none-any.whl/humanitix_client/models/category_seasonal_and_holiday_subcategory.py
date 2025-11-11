from enum import Enum


class CategorySeasonalAndHolidaySubcategory(str, Enum):
    AUTUMNEVENTS = "autumnEvents"
    CHRISTMAS = "christmas"
    EASTER = "easter"
    HALLOWEENHAUNT = "halloweenHaunt"
    HANUKKAH = "hanukkah"
    INDEPENDENCEDAY = "independenceDay"
    NEWYEARSEVE = "newYearsEve"
    OTHER = "other"
    STPATRICKSDAY = "stPatricksDay"
    THANKSGIVING = "thanksgiving"

    def __str__(self) -> str:
        return str(self.value)
