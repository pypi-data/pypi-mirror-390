from enum import Enum


class CategoryCharityAndCausesSubcategory(str, Enum):
    ANIMALWELFARE = "animalWelfare"
    DISASTERRELIEF = "disasterRelief"
    EDUCATION = "education"
    ENVIRONMENT = "environment"
    HEALTHCARE = "healthcare"
    HUMANRIGHTS = "humanRights"
    INTERNATIONALAID = "internationalAid"
    OTHER = "other"
    POVERTY = "poverty"

    def __str__(self) -> str:
        return str(self.value)
