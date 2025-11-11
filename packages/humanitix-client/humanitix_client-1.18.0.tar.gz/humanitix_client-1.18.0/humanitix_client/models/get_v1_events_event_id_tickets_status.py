from enum import Enum


class GetV1EventsEventIdTicketsStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
