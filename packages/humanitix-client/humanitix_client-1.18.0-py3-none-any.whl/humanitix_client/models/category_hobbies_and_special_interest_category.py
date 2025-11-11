from enum import Enum


class CategoryHobbiesAndSpecialInterestCategory(str, Enum):
    HOBBIESANDSPECIALINTEREST = "hobbiesAndSpecialInterest"

    def __str__(self) -> str:
        return str(self.value)
