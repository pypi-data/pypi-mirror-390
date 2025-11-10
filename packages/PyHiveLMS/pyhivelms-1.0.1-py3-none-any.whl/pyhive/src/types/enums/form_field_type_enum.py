"""Enumeration for form field types (auto-generated)."""

from enum import Enum


class FormFieldTypeEnum(str, Enum):
    """Enumeration of possible form field types."""

    MULTIPLE = "multiple"
    MULTIRESPONSE = "multiResponse"
    NUMBER = "number"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
