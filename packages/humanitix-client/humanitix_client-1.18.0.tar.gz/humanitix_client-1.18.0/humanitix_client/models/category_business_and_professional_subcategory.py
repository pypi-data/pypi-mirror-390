from enum import Enum


class CategoryBusinessAndProfessionalSubcategory(str, Enum):
    CAREER = "career"
    DESIGN = "design"
    EDUCATORS = "educators"
    ENVIRONMENTANDSUSTAINABILITY = "environmentAndSustainability"
    FINANCE = "finance"
    INVESTMENT = "investment"
    MEDIA = "media"
    NONPROFITNGO = "nonProfitNGO"
    OTHER = "other"
    REALESTATE = "realEstate"
    SALESANDMARKETING = "salesAndMarketing"
    STARTUPSANDBUSINESS = "startupsAndBusiness"

    def __str__(self) -> str:
        return str(self.value)
