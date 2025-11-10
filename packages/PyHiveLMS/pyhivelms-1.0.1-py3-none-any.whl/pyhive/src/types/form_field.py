"""Model definition for a form field used in questionnaires or structured input forms within Hive.

Represents a field definition with constraints and metadata,
including optional validation and visibility toggles.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define, field

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.form_field_type_enum import FormFieldTypeEnum

if TYPE_CHECKING:
    from ...client import HiveClient
    from .program import Class

T = TypeVar("T", bound="FormField")


@define
class FormField(HiveCoreItem):
    """Represents a single field in a dynamic form.

    Attributes:
        id: Field ID.
        name: Name of the field.
        type_: Field type (e.g., text, number, multiple).
        order: Position of the field in the form.
        required: Whether this field must be filled out.
        staff_responses: Whether staff members can respond.
        hanich_responses: Whether students can respond.
        has_value: Whether the field currently holds a value.
        segel_only: Whether the field is visible only to Segel (staff).
        description: Optional description of the field.
        lower_limit: Optional lower numeric limit.
        upper_limit: Optional upper numeric limit.
        choices: Optional list of string choices (for multiple/multiResponse).
        metadata: Additional arbitrary metadata for the field.
        groups: Optional list of group IDs the field is associated with.

    """

    hive_client: "HiveClient"
    id: int
    name: str
    type_: FormFieldTypeEnum
    order: int
    required: bool
    staff_responses: bool
    hanich_responses: bool
    has_value: bool
    segel_only: bool
    description: Unset | str = UNSET
    lower_limit: None | Unset | int = UNSET
    upper_limit: None | Unset | int = UNSET
    choices: None | Unset | list[str] = UNSET
    metadata: Unset | Any = UNSET
    group_ids: Unset | list[int] = UNSET
    _groups: "list[Class] | None" = field(init=False, default=None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type_.value,
            "order": self.order,
            "required": self.required,
            "staff_responses": self.staff_responses,
            "hanich_responses": self.hanich_responses,
            "has_value": self.has_value,
            "segel_only": self.segel_only,
            **(
                {"description": self.description}
                if self.description is not UNSET
                else {}
            ),
            **(
                {"lower_limit": self.lower_limit}
                if self.lower_limit is not UNSET
                else {}
            ),
            **(
                {"upper_limit": self.upper_limit}
                if self.upper_limit is not UNSET
                else {}
            ),
            **({"choices": self.choices} if self.choices is not UNSET else {}),
            **({"metadata": self.metadata} if self.metadata is not UNSET else {}),
            **({"groups": self.group_ids} if self.group_ids is not UNSET else {}),
        }

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        d = dict(src_dict)

        def _parse_optional_int(data: object) -> None | Unset | int:
            if data is None or isinstance(data, Unset):
                return data
            return cast("int", data)

        def _parse_choices(data: object) -> None | Unset | list[str]:
            if data is None or isinstance(data, Unset):
                return data
            if not isinstance(data, list):
                return UNSET
            return cast("list[str]", data)

        return cls(
            hive_client=hive_client,
            id=d.pop("id"),
            name=d.pop("name"),
            type_=FormFieldTypeEnum(d.pop("type")),
            order=d.pop("order"),
            required=d.pop("required"),
            staff_responses=d.pop("staff_responses"),
            hanich_responses=d.pop("hanich_responses"),
            has_value=d.pop("has_value"),
            segel_only=d.pop("segel_only"),
            description=d.pop("description", UNSET),
            lower_limit=_parse_optional_int(d.pop("lower_limit", UNSET)),
            upper_limit=_parse_optional_int(d.pop("upper_limit", UNSET)),
            choices=_parse_choices(d.pop("choices", UNSET)),
            metadata=d.pop("metadata", UNSET),
            group_ids=cast("Unset | list[int]", d.pop("groups", UNSET)),
        )

    @property
    def groups(self) -> list["Class"]:
        """Return the list of Classes which this field is relevant to."""
        if isinstance(self.group_ids, Unset):
            return []
        if self._groups is None:
            self._groups = [
                self.hive_client.get_class(group_id) for group_id in self.group_ids
            ]
        return self._groups

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, FormField):
            return False
        return self.id == value.id

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, FormField):
            return NotImplemented
        return self.order < value.order

    def __hash__(self) -> int:
        return hash((self.id,))
