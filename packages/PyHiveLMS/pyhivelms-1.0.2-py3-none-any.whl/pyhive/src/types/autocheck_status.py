"""AutoCheckStatus type definition."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define
from dateutil.parser import isoparse

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.action_enum import ActionEnum

if TYPE_CHECKING:
    from ...client import HiveClient

T = TypeVar("T", bound="AutoCheckStatus")


@define
class AutoCheckStatus(HiveCoreItem):
    """

    Attributes:
        id (int):
        time (datetime.datetime):
        action (ActionEnum):
            * `Handling` - Handling
            * `No Check` - Nocheck
            * `Built` - Built
            * `Finished` - Finished
            * `Sending` - Sending
            * `Error` - Error
            * `Success` - Success
        payload (Union[None, Unset, str]):

    """

    hive_client: "HiveClient"
    id: int
    time: datetime.datetime
    action: ActionEnum
    payload: Union[None, Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id
        time = self.time.isoformat()
        action = self.action.value
        payload: Union[None, Unset, str]

        if isinstance(self.payload, Unset):
            payload = UNSET
        else:
            payload = self.payload
        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "time": time,
                "action": action,
            }
        )

        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(
        cls: type[T],
        src_dict: Mapping[str, Any],
        hive_client: "HiveClient",
    ) -> T:
        d = dict(src_dict)
        id = d.pop("id")
        time = isoparse(d.pop("time"))
        action = ActionEnum(d.pop("action"))

        def _parse_payload(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        payload = _parse_payload(d.pop("payload", UNSET))

        return cls(
            hive_client=hive_client,
            id=id,
            time=time,
            action=action,
            payload=payload,
        )
