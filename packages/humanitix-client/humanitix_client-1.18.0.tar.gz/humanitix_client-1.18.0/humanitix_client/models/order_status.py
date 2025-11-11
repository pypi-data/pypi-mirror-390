from enum import Enum


class OrderStatus(str, Enum):
    COMPLETE = "complete"

    def __str__(self) -> str:
        return str(self.value)
