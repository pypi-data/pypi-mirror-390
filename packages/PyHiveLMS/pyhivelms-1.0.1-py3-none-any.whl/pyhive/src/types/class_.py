"""
Defines the Class type representing a school class/group in a program,
including serialization and lazy-loading of related objects.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define, field

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.class_type_enum import ClassTypeEnum

if TYPE_CHECKING:
    from ...client import HiveClient
    from .program import Program
    from .user import User

T = TypeVar("T", bound="Class")


@define
class Class(HiveCoreItem):
    """Represents a school class/group in a program.

    Attributes:
        id: Unique class ID.
        name: Internal name.
        display_name: Display name for UI.
        program_id: ID of the associated program.
        user_ids: List of user IDs assigned to this class.
        program_name: Name of the program.
        email: Optional class email address.
        type_: Type of class, e.g., Room or Student Group.
        description: Optional description text.

    """

    hive_client: "HiveClient"
    id: int
    name: str
    display_name: str
    program_id: int
    user_ids: list[int]
    program_name: str
    email: Unset | str = UNSET
    type_: Unset | ClassTypeEnum = UNSET
    description: None | Unset | str = UNSET

    # Lazy-loaded fields
    _program: "Program | None" = field(init=False, default=None)
    _users: "list[User] | None" = field(init=False, default=None)

    @property
    def program(self) -> "Program":
        """Lazily load the associated Program object."""
        if self._program is None:
            self._program = self.hive_client.get_program(self.program_id)
        return self._program

    @property
    def users(self) -> list["User"]:
        """Lazily load the list of User objects in this class."""
        if self._users is None:
            self._users = [self.hive_client.get_user(uid) for uid in self.user_ids]
        return self._users

    def to_dict(self) -> dict[str, Any]:
        """Serialize Class to dictionary form."""
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "program": self.program_id,
            "users": self.user_ids,
            "program__name": self.program_name,
        }

        if not isinstance(self.email, Unset):
            result["email"] = self.email
        if not isinstance(self.type_, Unset):
            result["type"] = self.type_.value
        if not isinstance(self.description, Unset):
            result["description"] = self.description

        return result

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        """Deserialize Class from dictionary form."""
        d = dict(src_dict)

        return cls(
            hive_client=hive_client,
            id=d["id"],
            name=d["name"],
            display_name=d["display_name"],
            program_id=d["program"],
            user_ids=cast("list[int]", d["users"]),
            program_name=d["program__name"],
            email=d.get("email", UNSET),
            type_=(
                UNSET
                if isinstance((type_val := d.get("type", UNSET)), Unset)
                else ClassTypeEnum(type_val)
            ),
            description=cast("None | Unset | str", d.get("description", UNSET)),
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Class):
            return False
        return self.id == value.id and self.program_id == value.program_id

ClassLike = TypeVar("ClassLike", Class, int)
