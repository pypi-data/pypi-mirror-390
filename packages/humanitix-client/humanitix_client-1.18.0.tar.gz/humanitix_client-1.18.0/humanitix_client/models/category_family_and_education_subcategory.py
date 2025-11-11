from enum import Enum


class CategoryFamilyAndEducationSubcategory(str, Enum):
    ALUMNI = "alumni"
    BABY = "baby"
    CHILDRENANDYOUTH = "childrenAndYouth"
    EDUCATION = "education"
    OTHER = "other"
    PARENTING = "parenting"
    PARENTSASSOCIATION = "parentsAssociation"
    REUNION = "reunion"
    SENIORCITIZEN = "seniorCitizen"

    def __str__(self) -> str:
        return str(self.value)
