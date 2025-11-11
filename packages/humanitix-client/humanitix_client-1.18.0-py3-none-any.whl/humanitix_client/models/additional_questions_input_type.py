from enum import Enum


class AdditionalQuestionsInputType(str, Enum):
    DATE = "date"
    EMAIL = "email"
    FILE = "file"
    NUMBER = "number"
    TEXT = "text"
    URL = "url"

    def __str__(self) -> str:
        return str(self.value)
