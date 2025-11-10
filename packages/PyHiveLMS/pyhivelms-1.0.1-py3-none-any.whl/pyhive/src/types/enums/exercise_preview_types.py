"""Enumeration for exercise preview types.
This is the document type of the instructions for an exercise (auto-generated)."""

from enum import Enum


class ExercisePreviewTypes(str, Enum):
    """Exercise preview types."""

    DISABLED = "Disabled"
    MARKDOWN = "Markdown"
    PDF = "PDF"

    def __str__(self) -> str:
        return str(self.value)
