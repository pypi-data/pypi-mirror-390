from enum import Enum


class TicketStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
