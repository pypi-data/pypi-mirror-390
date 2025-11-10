"""Enumeration for event types (auto-generated)."""

from enum import Enum


class EventTypeEnum(str, Enum):
    """Enumeration of possible event types in the Hive system."""

    הרצאה = "הרצאה"  # pylint: disable=non-ascii-name
    עע = "עע"  # pylint: disable=non-ascii-name
    פתבס = "פתבס"  # pylint: disable=non-ascii-name

    def __str__(self) -> str:
        return str(self.value)
