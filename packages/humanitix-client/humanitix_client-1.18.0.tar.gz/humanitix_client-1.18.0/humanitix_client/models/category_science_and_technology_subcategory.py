from enum import Enum


class CategoryScienceAndTechnologySubcategory(str, Enum):
    BIOTECH = "biotech"
    HIGHTECH = "highTech"
    MEDICINE = "medicine"
    MOBILE = "mobile"
    OTHER = "other"
    ROBOTICS = "robotics"
    SCIENCE = "science"
    SOCIALMEDIA = "socialMedia"

    def __str__(self) -> str:
        return str(self.value)
