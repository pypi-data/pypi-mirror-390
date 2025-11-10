"""Module for EventColor type."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define

from .core_item import HiveCoreItem

if TYPE_CHECKING:
    from ...client import HiveClient

T = TypeVar("T", bound="EventColor")


@define
class EventColor(HiveCoreItem):
    """Attributes:
    id (int):
    name (str):
    color (str):

    """

    id: int
    name: str
    color: str
    hive_client: "HiveClient"

    def to_dict(self) -> dict[str, Any]:
        """Converts the EventColor instance to a dictionary."""
        id = self.id

        name = self.name

        color = self.color

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "color": color,
            },
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        """Creates an EventColor instance from a dictionary."""
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        color = d.pop("color")

        return cls(
            id=id,
            name=name,
            color=color,
            hive_client=hive_client,
        )
