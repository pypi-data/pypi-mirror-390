from enum import Enum


class CategoryFamilyAndEducationCategory(str, Enum):
    FAMILYANDEDUCATION = "familyAndEducation"

    def __str__(self) -> str:
        return str(self.value)
