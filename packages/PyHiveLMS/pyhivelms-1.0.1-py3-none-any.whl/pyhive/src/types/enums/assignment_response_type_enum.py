"""Enumeration for Assignment Response Types."""

from enum import Enum


class AssignmentResponseTypeEnum(str, Enum):
    """Enumeration of possible assignment response types."""

    AUTOCHECK = "AutoCheck"
    COMMENT = "Comment"
    DONE = "Done"
    REDO = "Redo"
    SUBMISSION = "Submission"
    WORK_IN_PROGRESS = "Work In Progress"

    def __str__(self) -> str:
        return str(self.value)
