"""StatusEnum class representing various user statuses."""

from enum import Enum


class StatusEnum(str, Enum):
    """Enumeration of user statuses."""

    HOME = "Home"
    MEDICAL = "Medical"
    PERSONAL_TALK = "Personal Talk"
    PRAYER = "Prayer"
    PRESENT = "Present"
    RAISED_HAND = "Raised Hand"
    ROOM = "Room"
    TOILET = "Toilet"
    TOILET_REQUEST = "Toilet Request"
    WORK_TALK = "Work Talk"

    def __str__(self) -> str:
        return str(self.value)
