from enum import Enum


class CreateOnlineEventLocationType(str, Enum):
    ONLINE = "online"

    def __str__(self) -> str:
        return str(self.value)
