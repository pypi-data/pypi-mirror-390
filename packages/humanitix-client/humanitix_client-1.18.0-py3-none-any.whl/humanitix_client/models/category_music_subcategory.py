from enum import Enum


class CategoryMusicSubcategory(str, Enum):
    ALTERNATIVE = "alternative"
    AMERICANA = "americana"
    BLUEGRASS = "bluegrass"
    BLUES = "blues"
    BLUESANDJAZZ = "bluesAndJazz"
    CLASSICAL = "classical"
    COUNTRY = "country"
    CULTURAL = "cultural"
    DJDANCE = "djDance"
    EDM = "edm"
    EDMELECTRONIC = "edmElectronic"
    ELECTRONIC = "electronic"
    EXPERIMENTAL = "experimental"
    FOLK = "folk"
    HIPHOPRAP = "hipHopRap"
    INDIE = "indie"
    JAZZ = "jazz"
    LATIN = "latin"
    METAL = "metal"
    OPERA = "opera"
    OTHER = "other"
    POP = "pop"
    PSYCHEDELIC = "psychedelic"
    PUNKHARDCORE = "punkHardcore"
    RANDB = "rAndB"
    REGGAE = "reggae"
    RELIGIOUSSPIRITUAL = "religiousSpiritual"
    ROCK = "rock"
    SINGERSONGWRITER = "singerSongwriter"
    TOP40 = "top40"
    WORLD = "world"

    def __str__(self) -> str:
        return str(self.value)
