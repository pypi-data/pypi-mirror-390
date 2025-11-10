"""Enumeration for gender types."""

from enum import Enum


class GenderEnum(str, Enum):
    """Enumeration of gender types."""

    FEMALE = "Female"
    MALE = "Male"
    NONBINARY = "NonBinary"

    def __str__(self) -> str:
        return str(self.value)
