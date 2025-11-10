from enum import Enum


class Scope(str, Enum):
    ADMIN = "admin"
    CONTROL = "control"
    MONITOR = "monitor"
    STATUS = "status"

    def __str__(self) -> str:
        return str(self.value)
