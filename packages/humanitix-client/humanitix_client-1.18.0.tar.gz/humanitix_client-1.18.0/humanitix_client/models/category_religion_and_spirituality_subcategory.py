from enum import Enum


class CategoryReligionAndSpiritualitySubcategory(str, Enum):
    AGNOSTICISM = "agnosticism"
    ATHEISM = "atheism"
    BUDDHISM = "buddhism"
    CHRISTIANITY = "christianity"
    EASTERNRELIGION = "easternReligion"
    FOLKRELIGIONS = "folkReligions"
    HINDUISM = "hinduism"
    ISLAM = "islam"
    JUDAISM = "judaism"
    MORMONISM = "mormonism"
    MYSTICISMANDOCCULT = "mysticismAndOccult"
    NEWAGE = "newAge"
    OTHER = "other"
    SHINTOISM = "shintoism"
    SIKHISM = "sikhism"
    UNAFFILIATED = "unaffiliated"

    def __str__(self) -> str:
        return str(self.value)
