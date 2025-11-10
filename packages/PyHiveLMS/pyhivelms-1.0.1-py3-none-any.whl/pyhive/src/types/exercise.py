"""Model for exercises in course modules."""

from typing import TYPE_CHECKING, Any, Generator, Self, TypeVar, cast

from attrs import define, field

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.exercise_patbas_enum import PatbasEnum
from .enums.exercise_preview_types import ExercisePreviewTypes
from .enums.sync_status_enum import SyncStatusEnum

if TYPE_CHECKING:
    from ...client import HiveClient
    from .assignment import Assignment
    from .module import Module
    from .subject import Subject

T = TypeVar("T", bound="Exercise")


@define
class Exercise(HiveCoreItem):
    """Represents an exercise in a course module.

    Attributes:
        id: Unique exercise ID.
        name: Exercise name.
        parent_module_id: ID of the module the exercise belongs to.
        parent_subject_id: ID of the subject the exercise belongs to.
        parent_module_name: Name of the module.
        parent_subject_symbol: Symbol of the subject.
        parent_subject_color: Color tag of the subject.
        download: Whether the exercise is downloadable.
        preview: The preview method.
        parent_subject_name: Name of the subject.
        parent_module_order: Display order of the module.
        order: Display order of the exercise.
        tags: List of tag strings.
        patbas: PATBAS mode.
        sync_status: Synchronization status.
        sync_message: Optional sync error message.
        segel_path: Path to the exercise on the staff network.
        patbas_preview: Optional preview type for PATBAS.
        patbas_download: Whether PATBAS allows download.
        is_lecture: Whether this is a lecture.
        style: Optional style.
        on_creation_data: Optional metadata used on creation.
        autocheck_tag: Optional tag for auto-checking.
        autodone: Whether it can be automatically marked done.
        expected_duration: Optional string representing duration.
        segel_brief: Optional brief description.

    """

    hive_client: "HiveClient"
    id: int
    name: str
    parent_module_id: int
    parent_subject_id: int
    parent_module_name: str
    parent_subject_symbol: str
    parent_subject_color: str
    download: bool
    preview: ExercisePreviewTypes
    parent_subject_name: str
    parent_module_order: str
    order: str
    tags: list[str]
    patbas: PatbasEnum
    sync_status: SyncStatusEnum
    sync_message: None | str
    segel_path: str
    patbas_preview: Unset | ExercisePreviewTypes = UNSET
    patbas_download: Unset | bool = UNSET
    is_lecture: Unset | bool = UNSET
    style: None | Unset | str = UNSET
    on_creation_data: Unset | Any = UNSET
    autocheck_tag: None | Unset | str = UNSET
    autodone: Unset | bool = UNSET
    expected_duration: None | Unset | str = UNSET
    segel_brief: Unset | str = UNSET

    _parent_module: "Module | None" = field(init=False, default=None)
    _parent_subject: "Subject | None" = field(init=False, default=None)

    @property
    def parent_module(self) -> "Module":
        """Lazily load the module this exercise belongs to."""
        if self._parent_module is None:
            self._parent_module = self.hive_client.get_module(self.parent_module_id)
        return self._parent_module

    @property
    def parent_subject(self) -> "Subject":
        """Lazily load the subject this exercise belongs to."""
        if self._parent_subject is None:
            self._parent_subject = self.hive_client.get_subject(self.parent_subject_id)
        return self._parent_subject

    def to_dict(self) -> dict[str, Any]:
        """Serialize the Exercise to a dictionary."""
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "parent_module": self.parent_module_id,
            "parent_subject": self.parent_subject_id,
            "parent_module_name": self.parent_module_name,
            "parent_subject_symbol": self.parent_subject_symbol,
            "parent_subject_color": self.parent_subject_color,
            "download": self.download,
            "preview": self.preview.value,
            "parent_subject_name": self.parent_subject_name,
            "parent_module_order": self.parent_module_order,
            "order": self.order,
            "tags": self.tags,
            "patbas": self.patbas.value,
            "sync_status": self.sync_status.value,
            "sync_message": self.sync_message,
            "segel_path": self.segel_path,
        }

        if not isinstance(self.patbas_preview, Unset):
            result["patbas_preview"] = self.patbas_preview.value
        if not isinstance(self.patbas_download, Unset):
            result["patbas_download"] = self.patbas_download
        if not isinstance(self.is_lecture, Unset):
            result["is_lecture"] = self.is_lecture
        if not isinstance(self.style, Unset):
            result["style"] = self.style
        if not isinstance(self.on_creation_data, Unset):
            result["on_creation_data"] = self.on_creation_data
        if not isinstance(self.autocheck_tag, Unset):
            result["autocheck_tag"] = self.autocheck_tag
        if not isinstance(self.autodone, Unset):
            result["autodone"] = self.autodone
        if not isinstance(self.expected_duration, Unset):
            result["expected_duration"] = self.expected_duration
        if not isinstance(self.segel_brief, Unset):
            result["segel_brief"] = self.segel_brief

        return result

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any], hive_client: "HiveClient") -> Self:
        """Deserialize Exercise from dictionary."""
        d = dict(src_dict)

        return cls(
            hive_client=hive_client,
            id=d["id"],
            name=d["name"],
            parent_module_id=d["parent_module"],
            parent_subject_id=d["parent_subject"],
            parent_module_name=d["parent_module_name"],
            parent_subject_symbol=d["parent_subject_symbol"],
            parent_subject_color=d["parent_subject_color"],
            download=d["download"],
            preview=ExercisePreviewTypes(d["preview"]),
            parent_subject_name=d["parent_subject_name"],
            parent_module_order=d["parent_module_order"],
            order=d["order"],
            tags=cast("list[str]", d["tags"]),
            patbas=PatbasEnum(d["patbas"]),
            sync_status=SyncStatusEnum(d["sync_status"]),
            sync_message=cast("str | None", d["sync_message"]),
            segel_path=d["segel_path"],
            patbas_preview=(
                UNSET
                if isinstance((val := d.get("patbas_preview", UNSET)), Unset)
                else ExercisePreviewTypes(val)
            ),
            patbas_download=d.get("patbas_download", UNSET),
            is_lecture=d.get("is_lecture", UNSET),
            style=cast("str | None | Unset", d.get("style", UNSET)),
            on_creation_data=d.get("on_creation_data", UNSET),
            autocheck_tag=cast("str | None | Unset", d.get("autocheck_tag", UNSET)),
            autodone=d.get("autodone", UNSET),
            expected_duration=cast(
                "str | None | Unset", d.get("expected_duration", UNSET)
            ),
            segel_brief=cast("str | Unset", d.get("segel_brief", UNSET)),
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Exercise):
            return False
        return self.id == value.id and self.parent_module == value.parent_module

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, Exercise):
            return NotImplemented
        return self.order < value.order

    def get_assignments(self) -> Generator["Assignment", None, None]:
        """Fetch all assignments associated with this exercise."""
        return self.hive_client.get_assignments(
            exercise__id=self.id,
            exercise__parent_module__id=self.parent_module_id,
            exercise__parent_module__parent_subject__id=self.parent_subject_id,
        )

    def __iter__(self) -> Generator["Assignment", None, None]:
        """Allow iteration over this Exercise to yield its assignments."""
        yield from self.get_assignments()

    def __hash__(self) -> int:
        return hash(
            (
                self.id,
                self.parent_module_id,
                self.parent_subject_id,
            )
        )


ExerciseLike = TypeVar("ExerciseLike", Exercise, int)
