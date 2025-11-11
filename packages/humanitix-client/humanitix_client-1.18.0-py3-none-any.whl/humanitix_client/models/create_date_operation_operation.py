from enum import Enum


class CreateDateOperationOperation(str, Enum):
    CREATE = "CREATE"

    def __str__(self) -> str:
        return str(self.value)
