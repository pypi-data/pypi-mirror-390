from enum import Enum


class CategoryFashionAndBeautySubcategory(str, Enum):
    ACCESSORIES = "accessories"
    BEAUTY = "beauty"
    BRIDAL = "bridal"
    FASHION = "fashion"
    OTHER = "other"

    def __str__(self) -> str:
        return str(self.value)
