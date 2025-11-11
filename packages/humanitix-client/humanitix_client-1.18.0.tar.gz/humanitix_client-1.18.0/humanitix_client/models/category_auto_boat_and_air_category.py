from enum import Enum


class CategoryAutoBoatAndAirCategory(str, Enum):
    AUTOBOATANDAIR = "autoBoatAndAir"

    def __str__(self) -> str:
        return str(self.value)
