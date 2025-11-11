from enum import Enum


class CategoryReligionAndSpiritualityCategory(str, Enum):
    RELIGIONANDSPIRITUALITY = "religionAndSpirituality"

    def __str__(self) -> str:
        return str(self.value)
