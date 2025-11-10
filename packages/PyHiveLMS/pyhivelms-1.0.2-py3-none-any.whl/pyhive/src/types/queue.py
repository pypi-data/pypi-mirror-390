"""Queue model for the Hive API (auto-generated).

This module contains the :class:`Queue` dataclass which represents a
queue entry returned by the Hive API. The class provides simple
serialization helpers and lazily-resolved relationship properties.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define, field

from .common import UNSET, Unset
from .core_item import HiveCoreItem

if TYPE_CHECKING:
    from ...client import HiveClient
    from .module import Module
    from .program import Program
    from .subject import Subject
    from .user import User

T = TypeVar("T", bound="Queue")


@define
class Queue(HiveCoreItem):
    """Queue model representing a student/program/module queue entry.

    Attributes mirror the API JSON keys; relationship properties (``user``,
    ``module``, ``subject``, ``program``) lazily load the referenced
    objects using the supplied ``hive_client``.
    """

    hive_client: "HiveClient"
    id: int
    name: str
    user_name: None | str
    subject_id: None | int
    subject_name: None | str
    subject_color: None | str
    subject_symbol: None | str
    module_name: None | str
    module_order: None | str
    program_id: int
    program_name: str
    description: None | Unset | str = UNSET

    module_id: None | Unset | int = UNSET
    user_id: None | Unset | int = UNSET

    _user: "User | None" = field(init=False, default=None)
    _module: "Module | None" = field(init=False, default=None)
    _subject: "Subject | None" = field(init=False, default=None)
    _program: "Program | None" = field(init=False, default=None)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary of this Queue.

        The returned mapping only includes optional keys when they are not
        :data:`UNSET`.
        """
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "subject_color": self.subject_color,
            "subject_symbol": self.subject_symbol,
            "module_id": self.module_id,
            "module_name": self.module_name,
            "module_order": self.module_order,
            "program_id": self.program_id,
            "program_name": self.program_name,
            **(
                {"description": self.description}
                if self.description is not UNSET
                else {}
            ),
            **({"module": self.module} if self.module is not UNSET else {}),
            **({"user": self.user} if self.user_id is not UNSET else {}),
        }

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        """Create a :class:`Queue` instance from a mapping (typically parsed JSON).

        Args:
            src_dict: Mapping with keys matching the API response.
            hive_client: Hive client used to lazily resolve relationships.

        Returns:
            A populated :class:`Queue` instance.
        """
        d = dict(src_dict)

        def _optional(data: object) -> Any:
            return data if not isinstance(data, Unset) else UNSET

        return cls(
            hive_client=hive_client,
            id=d.pop("id"),
            name=d.pop("name"),
            user_id=cast("None | int", d.pop("user_id")),
            user_name=cast("None | str", d.pop("user_name")),
            subject_id=cast("None | int", d.pop("subject_id")),
            subject_name=cast("None | str", d.pop("subject_name")),
            subject_color=cast("None | str", d.pop("subject_color")),
            subject_symbol=cast("None | str", d.pop("subject_symbol")),
            module_id=cast("None | int", d.pop("module_id")),
            module_name=cast("None | str", d.pop("module_name")),
            module_order=cast("None | str", d.pop("module_order")),
            program_id=d.pop("program_id"),
            program_name=d.pop("program_name"),
            description=_optional(d.pop("description", UNSET)),
        )

    @property
    def user(self) -> "User | None":
        """Lazily return the :class:`User` associated with this queue entry.

        Returns None when no user_id is set.
        """
        if self._user is None and isinstance(self.user_id, int):
            self._user = self.hive_client.get_user(self.user_id)
        return self._user

    @property
    def module(self) -> "Module | None":
        """Lazily return the :class:`Module` referenced by this queue entry.

        Returns None when no module_id is present.
        """
        if self._module is None and isinstance(self.module_id, int):
            self._module = self.hive_client.get_module(self.module_id)
        return self._module

    @property
    def subject(self) -> "Subject | None":
        """Return the resolved :class:`Subject` or None if not available."""
        if isinstance(self.subject_id, int):
            return self.hive_client.get_subject(self.subject_id)
        return None

    @property
    def program(self) -> "Program":
        """Return the resolved :class:`Program` for this queue entry."""
        return self.hive_client.get_program(self.program_id)

QueueLike = TypeVar("QueueLike", Queue, int)
