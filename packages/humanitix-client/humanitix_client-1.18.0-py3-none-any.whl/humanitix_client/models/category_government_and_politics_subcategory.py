from enum import Enum


class CategoryGovernmentAndPoliticsSubcategory(str, Enum):
    COUNTYMUNICIPALGOVERNMENT = "countyMunicipalGovernment"
    DEMOCRATICPARTY = "democraticParty"
    FEDERALGOVERNMENT = "federalGovernment"
    INTERNATIONALAFFAIRS = "internationalAffairs"
    MILITARY = "military"
    NATIONALSECURITY = "nationalSecurity"
    NONPARTISAN = "nonPartisan"
    OTHER = "other"
    OTHERPARTY = "otherParty"
    REPUBLICANPARTY = "republicanParty"
    STATEGOVERNMENT = "stateGovernment"

    def __str__(self) -> str:
        return str(self.value)
