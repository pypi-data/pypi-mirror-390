from enum import Enum


class CategoryCommunityAndCultureCategory(str, Enum):
    COMMUNITYANDCULTURE = "communityAndCulture"

    def __str__(self) -> str:
        return str(self.value)
