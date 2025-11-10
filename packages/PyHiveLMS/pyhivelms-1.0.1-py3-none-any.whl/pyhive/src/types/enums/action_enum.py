"""Enumeration of possible action states for auto-tests."""

from enum import Enum


class ActionEnum(str, Enum):
    """Enumeration of possible action states for auto-tests."""

    BUILT = "Built"
    ERROR = "Error"
    FINISHED = "Finished"
    HANDLING = "Handling"
    NO_CHECK = "No Check"
    SENDING = "Sending"
    SUCCESS = "Success"

    def __str__(self) -> str:
        return str(self.value)
