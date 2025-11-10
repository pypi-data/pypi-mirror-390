"""Help Status Enum"""

from enum import Enum


class HelpStatusEnum(str, Enum):
    """Help Status Enum"""

    OPEN = "Open"
    RESOLVED = "Resolved"

    def __str__(self) -> str:
        return str(self.value)
