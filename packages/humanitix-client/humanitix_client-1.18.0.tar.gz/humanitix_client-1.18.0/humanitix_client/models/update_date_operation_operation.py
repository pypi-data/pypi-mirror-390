from enum import Enum


class UpdateDateOperationOperation(str, Enum):
    UPDATE = "UPDATE"

    def __str__(self) -> str:
        return str(self.value)
