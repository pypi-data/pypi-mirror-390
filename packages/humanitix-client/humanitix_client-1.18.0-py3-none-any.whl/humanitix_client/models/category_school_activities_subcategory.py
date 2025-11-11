from enum import Enum


class CategorySchoolActivitiesSubcategory(str, Enum):
    AFTERSCHOOLCARE = "afterSchoolCare"
    DINNER = "dinner"
    FUNDRAISER = "fundRaiser"
    OTHER = "other"
    PARKING = "parking"
    PUBLICSPEAKER = "publicSpeaker"
    RAFFLE = "raffle"

    def __str__(self) -> str:
        return str(self.value)
