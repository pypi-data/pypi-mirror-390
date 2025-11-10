"""Enumeration for synchronization status (auto-generated)."""

from enum import Enum


class SyncStatusEnum(str, Enum):
    """Enumeration of possible synchronization statuses."""

    CREATING = "Creating"
    DELETING = "Deleting"
    ERROR = "Error"
    NORMAL = "Normal"

    def __str__(self) -> str:
        return str(self.value)
