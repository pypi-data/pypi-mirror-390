""" "This module contains the HelpResponseSegelNested class."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define
from dateutil.parser import isoparse

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.help_response_type_enum import HelpResponseTypeEnum

if TYPE_CHECKING:
    from ...client import HiveClient

T = TypeVar("T", bound="HelpResponseSegelNested")


@define
class HelpResponseSegelNested(HiveCoreItem):
    """Attributes:
    id (int):
    user (int):
    date (datetime.datetime):
    response_type (HelpResponseTypeEnum):
        * `Resolve` - Resolve
        * `Open` - Open
        * `Comment` - Comment
    contents (Union[None, Unset, str]):
    file_name (Union[Unset, str]):
    dear_student (Union[Unset, bool]):  Default: True.
    hide_checker_name (Union[Unset, bool]):
    segel_only (Union[Unset, bool]):

    """

    hive_client: "HiveClient"
    id: int
    user: int
    date: datetime.datetime
    response_type: HelpResponseTypeEnum
    contents: None | Unset | str = UNSET
    file_name: Unset | str = UNSET
    dear_student: Unset | bool = True
    hide_checker_name: Unset | bool = UNSET
    segel_only: Unset | bool = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user = self.user

        date = self.date.isoformat()

        response_type = self.response_type.value

        contents: None | Unset | str
        contents = UNSET if isinstance(self.contents, Unset) else self.contents

        file_name = self.file_name

        dear_student = self.dear_student

        hide_checker_name = self.hide_checker_name

        segel_only = self.segel_only

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "user": user,
                "date": date,
                "response_type": response_type,
            },
        )
        if contents is not UNSET:
            field_dict["contents"] = contents
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if dear_student is not UNSET:
            field_dict["dear_student"] = dear_student
        if hide_checker_name is not UNSET:
            field_dict["hide_checker_name"] = hide_checker_name
        if segel_only is not UNSET:
            field_dict["segel_only"] = segel_only

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        user = d.pop("user")

        date = isoparse(d.pop("date"))

        response_type = HelpResponseTypeEnum(d.pop("response_type"))

        def _parse_contents(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | str", data)

        contents = _parse_contents(d.pop("contents", UNSET))

        file_name = d.pop("file_name", UNSET)

        dear_student = d.pop("dear_student", UNSET)

        hide_checker_name = d.pop("hide_checker_name", UNSET)

        segel_only = d.pop("segel_only", UNSET)

        return cls(
            id=id,
            user=user,
            date=date,
            response_type=response_type,
            contents=contents,
            file_name=file_name,
            dear_student=dear_student,
            hide_checker_name=hide_checker_name,
            segel_only=segel_only,
            hive_client=hive_client,
        )
