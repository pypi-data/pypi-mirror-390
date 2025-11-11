from enum import Enum


class CategoryPerformingAndVisualArtsSubcategory(str, Enum):
    BALLET = "ballet"
    COMEDY = "comedy"
    CRAFT = "craft"
    DANCE = "dance"
    DESIGN = "design"
    FINEART = "fineArt"
    JEWELRY = "jewelry"
    LITERARYARTS = "literaryArts"
    MUSICAL = "musical"
    OPERA = "opera"
    ORCHESTRA = "orchestra"
    OTHER = "other"
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    THEATRE = "theatre"

    def __str__(self) -> str:
        return str(self.value)
