from enum import Enum


class CategoryFilmMediaAndEntertainmentSubcategory(str, Enum):
    ADULT = "adult"
    ANIME = "anime"
    COMEDY = "comedy"
    COMICS = "comics"
    FILM = "film"
    GAMING = "gaming"
    OTHER = "other"
    TV = "tv"

    def __str__(self) -> str:
        return str(self.value)
