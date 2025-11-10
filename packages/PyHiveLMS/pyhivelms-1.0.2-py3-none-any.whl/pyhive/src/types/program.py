"""Model definition for the Hive Program entity.

Represents an educational program, including checker configuration,
sync status, and automatic handling flags.
"""

from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Any, Iterable, Self, TypeVar

from attrs import define, field

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.sync_status_enum import SyncStatusEnum
from .subject import Subject

if TYPE_CHECKING:
    from ...client import HiveClient
    from .class_ import Class
    from .user import User

T = TypeVar("T", bound="Program")


@define
class Program(HiveCoreItem):
    """Course Program entity.

    Attributes:
        id: Unique identifier.
        name: Display name of the program.
        checker_id: User ID of the assigned checker.
        sync_status: Sync status (e.g., Normal, Creating).
        sync_message: Optional sync diagnostic message.
        default_class_id: Optional class ID used as default.
        auto_toilet: Auto-toilet generation enabled.
        hanich_raise_hand: Whether hanich can raise hand.
        auto_schedule: Enable auto-scheduling.
        auto_room: Enable automatic room assignments.
        hanich_day_only: Restrict hanich to day-only usage.
        hanich_work_name: Enable work name customization.
        auto_toilet_count: Number of auto toilets to assign.
        hanich_classes_only: Restrict hanich to classes only.
        hanich_schedule: Whether hanich gets scheduled.

    """

    hive_client: "HiveClient"
    id: int
    name: str
    checker_id: int
    sync_status: SyncStatusEnum
    sync_message: None | str
    default_class_id: None | Unset | int

    auto_toilet: Unset | bool = UNSET
    hanich_raise_hand: Unset | bool = UNSET
    auto_schedule: Unset | bool = UNSET
    auto_room: Unset | bool = UNSET
    hanich_day_only: Unset | bool = UNSET
    hanich_work_name: Unset | bool = UNSET
    auto_toilet_count: Unset | int = UNSET
    hanich_classes_only: Unset | bool = UNSET
    hanich_schedule: Unset | bool = UNSET

    _checker: "User | None" = field(init=False, default=None)
    _default_class: "Class | None" = field(init=False, default=None)

    def __str__(self) -> str:
        return f"<Program[{self.id}] {self.name}>"

    @property
    def checker(self) -> "User":
        """Lazily loads and returns the checker (staff member)."""
        if self._checker is None:
            self._checker = self.hive_client.get_user(self.checker_id)
        return self._checker

    @property
    def default_class(self) -> "Class | None":
        """Lazily loads the default class, if set."""
        if (
            self._default_class is None
            and not isinstance(self.default_class_id, Unset)
            and self.default_class_id is not None
        ):
            self._default_class = self.hive_client.get_class(self.default_class_id)
        return self._default_class

    def get_subjects(self) -> Iterable[Subject]:
        """Returns all subjects belonging to this program."""
        return self.hive_client.get_subjects(parent_program__id__in=[self.id])

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "checker": self.checker_id,
            "sync_status": self.sync_status.value,
            "sync_message": self.sync_message,
        }

        if not isinstance(self.default_class_id, Unset):
            field_dict["default_class"] = self.default_class_id
        if not isinstance(self.auto_toilet, Unset):
            field_dict["auto_toilet"] = self.auto_toilet
        if not isinstance(self.hanich_raise_hand, Unset):
            field_dict["hanich_raise_hand"] = self.hanich_raise_hand
        if not isinstance(self.auto_schedule, Unset):
            field_dict["auto_schedule"] = self.auto_schedule
        if not isinstance(self.auto_room, Unset):
            field_dict["auto_room"] = self.auto_room
        if not isinstance(self.hanich_day_only, Unset):
            field_dict["hanich_day_only"] = self.hanich_day_only
        if not isinstance(self.hanich_work_name, Unset):
            field_dict["hanich_work_name"] = self.hanich_work_name
        if not isinstance(self.auto_toilet_count, Unset):
            field_dict["auto_toilet_count"] = self.auto_toilet_count
        if not isinstance(self.hanich_classes_only, Unset):
            field_dict["hanich_classes_only"] = self.hanich_classes_only
        if not isinstance(self.hanich_schedule, Unset):
            field_dict["hanich_schedule"] = self.hanich_schedule

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        """Create an instance of the class from a dictionary representation.

        Args:
            src_dict (Mapping[str, Any]): The source dictionary containing the data to populate the instance.
            hive_client (HiveClient): An instance of HiveClient to associate with the created object.

        Returns:
            Self: An instance of the class populated with data from src_dict.

        Notes:
            - Handles optional and unset fields using the _parse_optional helper.
            - Converts the 'sync_status' field to a SyncStatusEnum.
            - Pops fields from the dictionary to avoid duplication.

        """
        d = dict(src_dict)

        def _parse_optional(data: object) -> Any:
            if data is None or isinstance(data, Unset):
                return data
            return data

        return cls(
            id=d.pop("id"),
            name=d.pop("name"),
            checker_id=d.pop("checker"),
            sync_status=SyncStatusEnum(d.pop("sync_status")),
            sync_message=_parse_optional(d.pop("sync_message")),
            default_class_id=_parse_optional(d.pop("default_class", UNSET)),
            auto_toilet=d.pop("auto_toilet", UNSET),
            hanich_raise_hand=d.pop("hanich_raise_hand", UNSET),
            auto_schedule=d.pop("auto_schedule", UNSET),
            auto_room=d.pop("auto_room", UNSET),
            hanich_day_only=d.pop("hanich_day_only", UNSET),
            hanich_work_name=d.pop("hanich_work_name", UNSET),
            auto_toilet_count=d.pop("auto_toilet_count", UNSET),
            hanich_classes_only=d.pop("hanich_classes_only", UNSET),
            hanich_schedule=d.pop("hanich_schedule", UNSET),
            hive_client=hive_client,
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Program):
            return False
        return (
            self.id == value.id
            and self.checker_id == value.checker_id
            and self.name == value.name
        )

    def __iter__(self) -> Generator["Subject", None, None]:
        """Allow iteration over this Program to yield its subjects."""
        yield from self.get_subjects()

    def delete(self) -> None:
        self.hive_client.delete_program(self.id)


ProgramLike = TypeVar("ProgramLike", Program, int)
