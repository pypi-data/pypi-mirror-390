"""Model definition for help responses in the Hive system.

Represents a reply to a help request, which may include resolution,
comments, attachments, and display preferences.
"""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define, field
from dateutil.parser import isoparse

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.help_response_type_enum import HelpResponseTypeEnum

if TYPE_CHECKING:
    from ...client import HiveClient
    from .user import User

T = TypeVar("T", bound="HelpResponse")


@define
class HelpResponse(HiveCoreItem):
    """A response to a help request.

    Attributes:
        id: Unique identifier for the response.
        user: ID of the responding user.
        date: Timestamp of the response.
        response_type: Type of the response (e.g., Resolve, Open, Comment).
        contents: Optional text content of the response.
        file_name: Optional name of an attached file.
        dear_student: Whether to include a "Dear student" greeting. Default is True.
        hide_checker_name: If True, the name of the checker is hidden.
        segel_only: If True, the response is visible only to staff.

    """

    hive_client: "HiveClient"
    id: int
    user_id: int
    date: datetime.datetime
    response_type: HelpResponseTypeEnum
    contents: None | Unset | str = UNSET
    file_name: Unset | str = UNSET
    dear_student: Unset | bool = True
    hide_checker_name: Unset | bool = UNSET
    segel_only: Unset | bool = UNSET

    # Lazy-loaded objects
    _user: "User | None" = field(init=False, default=None)

    @property
    def user(self) -> "User":
        """Returns the User object associated with this instance.

        If the User object has not been retrieved yet,
         it fetches the user using the hive_client and caches it for future calls.

        Returns:
            User: The user associated with this instance.

        """
        if self._user is None:
            self._user = self.hive_client.get_user(self.user_id)
        return self._user

    def to_dict(self) -> dict[str, Any]:
        contents = UNSET if isinstance(self.contents, Unset) else self.contents

        field_dict: dict[str, Any] = {
            "id": self.id,
            "user": self.user_id,
            "date": self.date.isoformat(),
            "response_type": self.response_type.value,
        }
        if contents is not UNSET:
            field_dict["contents"] = contents
        if self.file_name is not UNSET:
            field_dict["file_name"] = self.file_name
        if self.dear_student is not UNSET:
            field_dict["dear_student"] = self.dear_student
        if self.hide_checker_name is not UNSET:
            field_dict["hide_checker_name"] = self.hide_checker_name
        if self.segel_only is not UNSET:
            field_dict["segel_only"] = self.segel_only

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any], hive_client: "HiveClient") -> Self:
        d = dict(src_dict)

        def _parse_optional_str(data: object) -> None | Unset | str:
            if data is None or isinstance(data, Unset):
                return data
            return cast("str", data)

        return cls(
            hive_client=hive_client,
            id=d.pop("id"),
            user_id=d.pop("user"),
            date=isoparse(d.pop("date")),
            response_type=HelpResponseTypeEnum(d.pop("response_type")),
            contents=_parse_optional_str(d.pop("contents", UNSET)),
            file_name=d.pop("file_name", UNSET),
            dear_student=d.pop("dear_student", UNSET),
            hide_checker_name=d.pop("hide_checker_name", UNSET),
            segel_only=d.pop("segel_only", UNSET),
        )
