from enum import Enum


class CategoryMusicCategory(str, Enum):
    MUSIC = "music"

    def __str__(self) -> str:
        return str(self.value)
