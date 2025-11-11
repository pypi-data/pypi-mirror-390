from enum import Enum


class CategoryFashionAndBeautyCategory(str, Enum):
    FASHIONANDBEAUTY = "fashionAndBeauty"

    def __str__(self) -> str:
        return str(self.value)
