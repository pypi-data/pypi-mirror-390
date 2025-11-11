from enum import Enum


class DeleteDateOperationOperation(str, Enum):
    DELETE = "DELETE"

    def __str__(self) -> str:
        return str(self.value)
