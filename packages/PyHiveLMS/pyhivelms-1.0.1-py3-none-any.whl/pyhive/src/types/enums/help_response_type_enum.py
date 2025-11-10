"""Enumeration for help response types (auto-generated)."""

from enum import Enum


class HelpResponseTypeEnum(str, Enum):
    """Enumeration of possible help response types."""

    COMMENT = "Comment"
    OPEN = "Open"
    RESOLVE = "Resolve"

    def __str__(self) -> str:
        return str(self.value)
