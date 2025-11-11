from enum import Enum


class EventLocationType(str, Enum):
    ADDRESS = "address"
    CUSTOM = "custom"
    ONLINE = "online"
    TOBEANNOUNCED = "toBeAnnounced"

    def __str__(self) -> str:
        return str(self.value)
