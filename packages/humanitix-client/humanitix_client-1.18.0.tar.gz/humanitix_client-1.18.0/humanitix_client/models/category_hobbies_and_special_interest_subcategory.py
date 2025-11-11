from enum import Enum


class CategoryHobbiesAndSpecialInterestSubcategory(str, Enum):
    ADULT = "adult"
    ANIMECOMICS = "animeComics"
    BOOKS = "books"
    DIY = "diy"
    DRAWINGANDPAINTING = "drawingAndPainting"
    GAMING = "gaming"
    KNITTING = "knitting"
    OTHER = "other"
    PHOTOGRAPHY = "photography"

    def __str__(self) -> str:
        return str(self.value)
