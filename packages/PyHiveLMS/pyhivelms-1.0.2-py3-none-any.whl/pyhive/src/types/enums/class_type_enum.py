"""Enumeration of class types."""

from enum import Enum


class ClassTypeEnum(str, Enum):
    """Enumeration of class types."""

    ROOM = "Room"
    STUDENT_GROUP = "Student Group"

    def __str__(self) -> str:
        return str(self.value)
