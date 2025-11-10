"""Enumeration for user clearance levels."""

from enum import IntEnum


class ClearanceEnum(IntEnum):
    """Enumeration of user clearance levels in the Hive system."""

    HANICH = 1
    CHECKER = 2
    SEGEL = 3
    ADMIN = 5

    def __str__(self) -> str:
        return str(self.value)
