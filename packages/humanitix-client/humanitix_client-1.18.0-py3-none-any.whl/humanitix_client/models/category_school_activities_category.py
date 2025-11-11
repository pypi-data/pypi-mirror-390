from enum import Enum


class CategorySchoolActivitiesCategory(str, Enum):
    SCHOOLACTIVITIES = "schoolActivities"

    def __str__(self) -> str:
        return str(self.value)
