"""Enumeration for help request types (auto-generated)."""

from enum import Enum


class HelpTypeEnum(str, Enum):
    """Enumeration of possible help request types."""

    CHAT = "Chat"
    ERROR = "Error"
    EXERCISE = "Exercise"
    MEDICAL = "Medical"
    MUSIC = "Music"
    OTHER = "Other"
    REQUEST = "Request"

    def __str__(self) -> str:
        return str(self.value)
