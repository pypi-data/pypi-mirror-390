"""Type definitions for PyHiveLMS."""

from __future__ import annotations

# Import the implementation from the `pyhive` package (implementation
# lives there) and expose the client at package level.
from pyhive.src.types.assignment import Assignment
from pyhive.src.types.assignment_response import AssignmentResponse
from pyhive.src.types.class_ import Class
from pyhive.src.types.enums.clearance_enum import ClearanceEnum
from pyhive.src.types.enums.gender_enum import GenderEnum
from pyhive.src.types.exercise import Exercise
from pyhive.src.types.form_field import FormField
from pyhive.src.types.module import Module
from pyhive.src.types.program import Program
from pyhive.src.types.subject import Subject
from pyhive.src.types.user import User

__all__ = [
    "Assignment",
    "AssignmentResponse",
    "User",
    "Module",
    "Exercise",
    "Class",
    "FormField",
    "Subject",
    "Program",
    "ClearanceEnum",
    "GenderEnum",
]
