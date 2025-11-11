from enum import Enum


class SalesChannel(str, Enum):
    MANUAL = "manual"
    ONLINE = "online"

    def __str__(self) -> str:
        return str(self.value)
