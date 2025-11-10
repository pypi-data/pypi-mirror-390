"""Hive management course user type."""

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Iterable, Self, TypeVar, cast

from attrs import define, field
from dateutil.parser import isoparse

from .common import UNSET, Unset
from .core_item import HiveCoreItem
from .enums.clearance_enum import ClearanceEnum
from .enums.gender_enum import GenderEnum
from .enums.status_enum import StatusEnum

if TYPE_CHECKING:
    from ...client import HiveClient
    from .assignment import Assignment
    from .class_ import Class
    from .program import Program
    from .queue import Queue

T = TypeVar("T", bound="User")


@define
class User(HiveCoreItem):  # pylint: disable=too-many-instance-attributes
    """Hive management course user.

    Attributes:
    id (int):
    display_name (str):
    clearance (ClearanceEnum):
        * `1` - Hanich
        * `2` - Checker
        * `3` - Segel
        * `5` - Admin
    gender (GenderEnum):
        * `Male` - Male
        * `Female` - Female
        * `NonBinary` - Nonbinary
    current_assignment (Union[None, int]):
    current_assignment_options (list[int]):
    mentee_ids (list[int]):
    username (str): Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
    status (StatusEnum):
        * `Present` - Present
        * `Raised Hand` - Raisedhand
        * `Toilet Request` - Toiletrequest
        * `Toilet` - Toilet
        * `Personal Talk` - Personaltalk
        * `Work Talk` - Worktalk
        * `Medical` - Medical
        * `Prayer` - Prayer
        * `Room` - Room
        * `Home` - Home
    status_date (datetime.datetime):
    avatar_filename (Union[Unset, str]):
    number (Union[None, Unset, int]):
    program (Union[None, Unset, int]):
    checkers_brief (Union[Unset, str]):
    mentor (Union[None, Unset, int]):
    classes (Union[Unset, list[int]]):
    first_name (Union[Unset, str]):
    last_name (Union[Unset, str]):
    queue (Union[None, Unset, int]):
    disable_queue (Union[Unset, bool]):
    user_queue (Union[None, Unset, int]):
    disable_user_queue (Union[Unset, bool]):
    override_queue (Union[None, Unset, int]):
    confirmed (Union[Unset, bool]):
    teacher (Union[Unset, bool]):
    hostname (Union[Unset, str]):

    """

    hive_client: "HiveClient"
    id: int
    display_name: str
    clearance: ClearanceEnum
    gender: GenderEnum
    current_assignment_id: None | int
    _current_assignment: "Assignment | None" = field(init=False, default=None)
    current_assignment_options: list[int]
    mentee_ids: list[int]
    _mentees: "list[User] | None" = field(init=False, default=None)
    username: str
    status: StatusEnum
    status_date: datetime.datetime
    avatar_filename: Unset | str = UNSET
    number: None | Unset | int = UNSET
    program_id: None | Unset | int = UNSET
    _program: "Program | None" = field(init=False, default=None)
    checkers_brief: Unset | str = UNSET
    mentor_id: None | Unset | int = UNSET
    _mentor: "User | None" = field(init=False, default=None)
    class_ids: Unset | list[int] = UNSET
    _classes: "list[Class] | None" = field(init=False, default=None)
    first_name: Unset | str = UNSET
    last_name: Unset | str = UNSET
    queue_id: None | Unset | int = UNSET
    _queue: "Queue | None" = field(init=False, default=None)
    disable_queue: Unset | bool = UNSET
    user_queue_id: None | Unset | int = UNSET
    _user_queue: "Queue | None" = field(init=False, default=None)
    disable_user_queue: Unset | bool = UNSET
    override_queue_id: None | Unset | int = UNSET
    _override_queue: "Queue | None" = field(init=False, default=None)
    confirmed: Unset | bool = UNSET
    teacher: Unset | bool = UNSET
    hostname: Unset | str = UNSET

    def to_dict(  # pylint: disable=too-many-locals, too-many-statements, too-many-branches
        self,
    ) -> dict[str, Any]:
        id = self.id

        display_name = self.display_name

        clearance = self.clearance.value

        gender = self.gender.value

        current_assignment_id: None | int
        current_assignment_id = self.current_assignment_id

        current_assignment_options = self.current_assignment_options

        mentee_ids = self.mentee_ids

        username = self.username

        status = self.status.value

        status_date = self.status_date.isoformat()

        avatar_filename = self.avatar_filename

        number: None | Unset | int
        number = UNSET if isinstance(self.number, Unset) else self.number

        program_id: None | Unset | int
        program_id = UNSET if isinstance(self.program_id, Unset) else self.program_id

        checkers_brief = self.checkers_brief

        mentor_id: None | Unset | int
        mentor_id = UNSET if isinstance(self.mentor_id, Unset) else self.mentor_id

        class_ids: Unset | list[int] = UNSET
        if not isinstance(self.class_ids, Unset):
            class_ids = self.class_ids

        first_name = self.first_name

        last_name = self.last_name

        queue_id: None | Unset | int
        queue_id = UNSET if isinstance(self.queue_id, Unset) else self.queue_id

        disable_queue = self.disable_queue

        user_queue_id: None | Unset | int
        user_queue_id = (
            UNSET if isinstance(self.user_queue_id, Unset) else self.user_queue_id
        )

        disable_user_queue = self.disable_user_queue

        override_queue_id: None | Unset | int
        override_queue_id = (
            UNSET
            if isinstance(self.override_queue_id, Unset)
            else self.override_queue_id
        )

        confirmed = self.confirmed

        teacher = self.teacher

        hostname = self.hostname

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "display_name": display_name,
                "clearance": clearance,
                "gender": gender,
                "current_assignment": current_assignment_id,
                "current_assignment_options": current_assignment_options,
                "mentees": mentee_ids,
                "username": username,
                "status": status,
                "status_date": status_date,
            },
        )
        if avatar_filename is not UNSET:
            field_dict["avatar_filename"] = avatar_filename
        if number is not UNSET:
            field_dict["number"] = number
        if program_id is not UNSET:
            field_dict["program"] = program_id
        if checkers_brief is not UNSET:
            field_dict["checkers_brief"] = checkers_brief
        if mentor_id is not UNSET:
            field_dict["mentor"] = mentor_id
        if class_ids is not UNSET:
            field_dict["classes"] = class_ids
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if queue_id is not UNSET:
            field_dict["queue"] = queue_id
        if disable_queue is not UNSET:
            field_dict["disable_queue"] = disable_queue
        if user_queue_id is not UNSET:
            field_dict["user_queue"] = user_queue_id
        if disable_user_queue is not UNSET:
            field_dict["disable_user_queue"] = disable_user_queue
        if override_queue_id is not UNSET:
            field_dict["override_queue"] = override_queue_id
        if confirmed is not UNSET:
            field_dict["confirmed"] = confirmed
        if teacher is not UNSET:
            field_dict["teacher"] = teacher
        if hostname is not UNSET:
            field_dict["hostname"] = hostname

        return field_dict

    @classmethod
    def from_dict(  # pylint: disable=too-many-locals
        cls,
        src_dict: Mapping[str, Any],
        hive_client: "HiveClient",
    ) -> Self:
        """Deserialize a User instance from a mapping."""
        d = dict(src_dict)
        id = d.pop("id")

        display_name = d.pop("display_name")

        clearance = ClearanceEnum(d.pop("clearance"))

        gender = GenderEnum(d.pop("gender"))

        def _parse_current_assignment(data: object) -> None | int:
            if data is None:
                return data
            return cast("None | int", data)

        current_assignment = _parse_current_assignment(d.pop("current_assignment"))

        current_assignment_options = cast(
            "list[int]", d.pop("current_assignment_options")
        )

        mentee_ids = cast("list[int]", d.pop("mentees"))

        username = d.pop("username")

        status = StatusEnum(d.pop("status"))

        status_date = isoparse(d.pop("status_date"))

        avatar_filename = d.pop("avatar_filename", UNSET)

        def _parse_number(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        number = _parse_number(d.pop("number", UNSET))

        def _parse_program(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        program = _parse_program(d.pop("program", UNSET))

        checkers_brief = d.pop("checkers_brief", UNSET)

        def _parse_mentor(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        mentor = _parse_mentor(d.pop("mentor", UNSET))

        classes = cast("list[int]", d.pop("classes", UNSET))

        first_name = d.pop("first_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        def _parse_queue(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        queue = _parse_queue(d.pop("queue", UNSET))

        disable_queue = d.pop("disable_queue", UNSET)

        def _parse_user_queue(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        user_queue = _parse_user_queue(d.pop("user_queue", UNSET))

        disable_user_queue = d.pop("disable_user_queue", UNSET)

        def _parse_override_queue(data: object) -> None | Unset | int:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | int", data)

        override_queue = _parse_override_queue(d.pop("override_queue", UNSET))

        confirmed = d.pop("confirmed", UNSET)

        teacher = d.pop("teacher", UNSET)

        hostname = d.pop("hostname", UNSET)

        return cls(
            id=id,
            display_name=display_name,
            clearance=clearance,
            gender=gender,
            current_assignment_id=current_assignment,
            current_assignment_options=current_assignment_options,
            mentee_ids=mentee_ids,
            username=username,
            status=status,
            status_date=status_date,
            avatar_filename=avatar_filename,
            number=number,
            program_id=program,
            checkers_brief=checkers_brief,
            mentor_id=mentor,
            class_ids=classes,
            first_name=first_name,
            last_name=last_name,
            queue_id=queue,
            disable_queue=disable_queue,
            user_queue_id=user_queue,
            disable_user_queue=disable_user_queue,
            override_queue_id=override_queue,
            confirmed=confirmed,
            teacher=teacher,
            hostname=hostname,
            hive_client=hive_client,
        )

    @property
    def program(self) -> "Program | None":
        """The program this user is in."""
        if not isinstance(self.program_id, int):
            return None
        if self._program is None:
            self._program = self.hive_client.get_program(self.program_id)
        return self._program

    @property
    def mentees(self) -> list["User"]:
        """The mentees of this user."""
        if self._mentees is None:
            self._mentees = list(self.hive_client.get_users(id__in=self.mentee_ids))
        return self._mentees

    @property
    def mentor(self) -> "User | None":
        """The mentor of this user."""
        if not isinstance(self.mentor_id, int):
            return None
        if self._mentor is None:
            self._mentor = self.hive_client.get_user(self.mentor_id)
        return self._mentor

    @property
    def classes(self) -> list["Class"]:
        """The classes this user is in."""
        if self._classes is None:
            if isinstance(self.class_ids, Unset):
                self._classes = []
            else:
                self._classes = list(
                    self.hive_client.get_classes(id__in=self.class_ids)
                )
        return self._classes

    @property
    def queue(self) -> "Queue | None":
        """The queue this user is in."""
        if not isinstance(self.queue_id, int):
            return None
        if self._queue is None:
            self._queue = self.hive_client.get_queue(self.queue_id)
        return self._queue

    @property
    def user_queue(self) -> "Queue | None":
        """The user queue this user is in."""
        if not isinstance(self.user_queue_id, int):
            return None
        if self._user_queue is None:
            self._user_queue = self.hive_client.get_queue(self.user_queue_id)
        return self._user_queue

    @property
    def override_queue(self) -> "Queue | None":
        """The override queue this user is in."""
        if not isinstance(self.override_queue_id, int):
            return None
        if self._override_queue is None:
            self._override_queue = self.hive_client.get_queue(self.override_queue_id)
        return self._override_queue

    @property
    def current_assignment(self) -> "Assignment | None":
        """The current assignment of this user."""
        if not isinstance(self.current_assignment_id, int):
            return None
        if self._current_assignment is None:
            self._current_assignment = self.hive_client.get_assignment(
                self.current_assignment_id
            )
        return self._current_assignment

    def get_assignments(self) -> Iterable["Assignment"]:
        """Get all assignments for this user."""
        return self.hive_client.get_assignments(for_user=self)

    def delete(self) -> None:
        self.hive_client.delete_user(self.id)


UserLike = TypeVar("UserLike", User, int)
