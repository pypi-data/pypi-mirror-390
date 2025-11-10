"""Users mixin for HiveClient.

Provides listing and retrieval of user records from the management API.
"""

from typing import TYPE_CHECKING, Generator, Iterable, Optional

from ..client.utils import resolve_item_or_id
from ..src.types.enums.clearance_enum import ClearanceEnum
from ..src.types.user import User
from .client_shared import ClientCoreMixin

if TYPE_CHECKING:
    from ..src.types.class_ import ClassLike
    from ..src.types.program import ProgramLike
    from ..src.types.user import UserLike


class UserClientMixin(ClientCoreMixin):
    """Mixin that exposes user management endpoints (list, get, me)."""

    def get_users(  # pylint: disable=too-many-arguments
        self,
        *,
        classes__id__in: Optional[list[int]] = None,
        clearance__in: Optional[list[int]] = None,
        id__in: Optional[list[int]] = None,
        mentor__id: Optional[int] = None,
        mentor__id__in: Optional[list[int]] = None,
        program__id__in: Optional[list[int]] = None,
        program_checker__id__in: Optional[list[int]] = None,
    ) -> Generator[User, None, None]:
        """Yield users filtered by the provided criteria."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        return self._get_core_items(
            "/api/core/management/users/",
            User,
            classes__id__in=classes__id__in,
            clearance__in=clearance__in,
            id__in=id__in,
            mentor__id=mentor__id,
            mentor__id__in=mentor__id__in,
            program__id__in=program__id__in,
            program_checker__id__in=program_checker__id__in,
        )

    def get_user(self, user_id: int) -> User:
        """Return a single user by ``user_id``."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        return User.from_dict(
            self.get(f"/api/core/management/users/{user_id}/"),
            hive_client=self,
        )

    def get_user_me(self) -> User:  # pragma: no cover
        """Return the current user.

        Note: This endpoint is intentionally not implemented because it does not
        return the same shape as ``/users/{id}/`` in the current API.
        """
        raise NotImplementedError("get_user_me() is not implemented")
        # For some reason this endpoint does not return the same data as /users/{id}/
        # return User.from_dict(
        #     self.get("/api/core/management/users/me/"),
        #     hive_client=self,
        # )

    def get_students(
        self,
        *,
        of_mentor: Optional["UserLike"] = None,
        of_class: Optional["ClassLike"] = None,
        of_program: Optional["ProgramLike"] = None,
    ) -> Iterable[User]:
        yield from self.get_users(
            classes__id__in=[resolve_item_or_id(of_class)] if of_class else None,
            clearance__in=[ClearanceEnum.HANICH],
            mentor__id=resolve_item_or_id(of_mentor),
            program__id__in=[resolve_item_or_id(of_program)] if of_program else None,
        )

    def get_user_by_name(
        self,
        name: str,
        *,
        clearance: Optional[ClearanceEnum] = None,
    ) -> User | None:
        all_users = list(
            self.get_users(clearance__in=[clearance] if clearance else None)
        )
        # Try matching full user name
        users_matching_full_name = list(
            filter(
                lambda user: name
                in (
                    f"{user.first_name} {user.last_name}",
                    user.display_name,
                ),
                all_users,
            )
        )
        if users_matching_full_name == 1:
            # Perfect name match found
            # Note that this might fail on students ["אור דוד", "אור דוד כהן"]
            #  where we want the first student, whose first name happens
            #  to be exactly the full name of the second student
            # TODO: Handle names better?
            return users_matching_full_name[0]

        # Try matching only first name
        users_matching_first_name = list(
            filter(
                lambda user: user.first_name == name,
                all_users,
            )
        )

        if len(users_matching_first_name) > 1:
            raise RuntimeError("More than one user found matching given name!")
        return (
            users_matching_first_name[0] if len(users_matching_first_name) > 0 else None
        )

    def get_student(
        self, name: Optional[str] = None, number: Optional[int] = None
    ) -> User | None:
        if name is None and number is None:
            raise ValueError("Either name or number must be given!")

        if number is None:
            assert name is not None
            return self.get_user_by_name(name, clearance=ClearanceEnum.HANICH)

        assert number is not None

        all_students = list(self.get_students())

        students_matching_number = list(
            filter(lambda student: student.number == number, all_students)
        )

        if len(students_matching_number) == 0:
            return None

        students_perfect_match = []
        if name is not None:
            students_perfect_match = list(
                filter(
                    lambda student: name
                    in (
                        student.first_name,
                        student.last_name,
                        student.display_name,
                        f"{student.first_name} {student.last_name}",
                    ),
                    students_matching_number,
                )
            )

        if len(students_perfect_match) > 1:
            raise RuntimeError(
                "More than one student found matching given name and number!"
            )

        return students_perfect_match[0] if len(students_perfect_match) == 1 else None
