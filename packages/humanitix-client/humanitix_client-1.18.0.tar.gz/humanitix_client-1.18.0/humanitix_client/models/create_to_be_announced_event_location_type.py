from enum import Enum


class CreateToBeAnnouncedEventLocationType(str, Enum):
    TOBEANNOUNCED = "toBeAnnounced"

    def __str__(self) -> str:
        return str(self.value)
