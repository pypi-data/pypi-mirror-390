"""EventAttendeesType0Item type class module."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define

from .common import UNSET, Unset
from .core_item import HiveCoreItem

if TYPE_CHECKING:
    from ...client import HiveClient

T = TypeVar("T", bound="EventAttendeesType0Item")


@define
class EventAttendeesType0Item(HiveCoreItem):
    """Attributes:
    name (str):
    id (int):
    description (Union[Unset, str]):

    """

    hive_client: "HiveClient"
    name: str
    id: int
    description: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id = self.id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "id": id,
            },
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        d = dict(src_dict)
        name = d.pop("name")

        id = d.pop("id")

        description = d.pop("description", UNSET)

        return cls(
            name=name,
            id=id,
            description=description,
            hive_client=hive_client,
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, EventAttendeesType0Item):
            return False
        return self.id == value.id
