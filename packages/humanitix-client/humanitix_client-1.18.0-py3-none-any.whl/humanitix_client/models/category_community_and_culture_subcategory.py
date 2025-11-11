from enum import Enum


class CategoryCommunityAndCultureSubcategory(str, Enum):
    CITYTOWN = "cityTown"
    COUNTY = "county"
    HERITAGE = "heritage"
    HISTORIC = "historic"
    LANGUAGE = "language"
    LGBT = "lgbt"
    MEDIEVAL = "medieval"
    NATIONALITY = "nationality"
    OTHER = "other"
    RENAISSANCE = "renaissance"
    STATE = "state"

    def __str__(self) -> str:
        return str(self.value)
