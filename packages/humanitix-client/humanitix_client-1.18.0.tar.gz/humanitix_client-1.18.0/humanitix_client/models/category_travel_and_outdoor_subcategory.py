from enum import Enum


class CategoryTravelAndOutdoorSubcategory(str, Enum):
    CANOEING = "canoeing"
    CLIMBING = "climbing"
    HIKING = "hiking"
    KAYAKING = "kayaking"
    OTHER = "other"
    RAFTING = "rafting"
    TRAVEL = "travel"

    def __str__(self) -> str:
        return str(self.value)
