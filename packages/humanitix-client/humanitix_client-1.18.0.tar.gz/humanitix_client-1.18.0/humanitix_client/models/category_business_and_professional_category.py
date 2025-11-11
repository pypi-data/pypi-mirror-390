from enum import Enum


class CategoryBusinessAndProfessionalCategory(str, Enum):
    BUSINESSANDPROFESSIONAL = "businessAndProfessional"

    def __str__(self) -> str:
        return str(self.value)
