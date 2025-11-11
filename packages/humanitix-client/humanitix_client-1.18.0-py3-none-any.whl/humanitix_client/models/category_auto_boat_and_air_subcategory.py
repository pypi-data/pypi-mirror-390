from enum import Enum


class CategoryAutoBoatAndAirSubcategory(str, Enum):
    AIR = "air"
    AUTO = "auto"
    BOAT = "boat"
    MOTORCYCLE = "motorcycle"
    OTHER = "other"

    def __str__(self) -> str:
        return str(self.value)
