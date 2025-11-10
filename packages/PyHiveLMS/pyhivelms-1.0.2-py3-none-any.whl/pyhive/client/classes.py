"""
Class resource mixin for HiveClient.

Provides listing and retrieval of Class records from the Hive API. Use only as a mixin for the main HiveClient.
"""

from typing import TYPE_CHECKING, Iterable, Optional

from ..src.types.class_ import Class, ClassLike
from ..src.types.enums.class_type_enum import ClassTypeEnum
from .client_shared import ClientCoreMixin
from .utils import resolve_item_or_id

if TYPE_CHECKING:
    from ..src.types.program import ProgramLike
    from ..src.types.user import UserLike


class ClassesClientMixin(ClientCoreMixin):
    """
    Mixin class providing class-related API methods for HiveClient.

    Methods
    -------
    get_classes(id__in=None, name=None, program__id__in=None, type_=None, ...)
        List all or filtered classes via the Hive API. Supports multiple relationship filters.
    get_class(class_id)
        Retrieve a single class by id.
    """

    def get_classes(
        self,
        *,
        id__in: Optional[list[int]] = None,
        name: Optional[str] = None,
        program__id__in: Optional[list[int]] = None,
        type_: Optional[ClassTypeEnum] = None,
    ) -> Iterable[Class]:
        """Yield ``Class`` objects filtered by the provided criteria."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"
        return self._get_core_items(
            "/api/core/management/classes/",
            Class,
            id__in=id__in,
            name=name,
            program__id__in=program__id__in,
            type_=type_,
        )

    def get_class(
        self,
        class_id: int,
    ) -> Class:
        """Return a single ``Class`` by its id."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"
        return Class.from_dict(
            self.get(f"/api/core/management/classes/{class_id}/"),
            hive_client=self,
        )

    def create_class(
        self,
        name: str,
        *,
        program: "ProgramLike",
        users: Optional[list["UserLike"]] = None,
        email: Optional[str] = None,
        type_: Optional[ClassTypeEnum] = None,
        classes: Optional[list["ClassLike"]] = None,
        description: Optional[str] = None,
    ) -> Class:
        """
        Create a Class via the Hive API.
        """

        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        payload: dict[str, object] = {
            "name": name,
            "program": resolve_item_or_id(program),
        }

        # Users list - include always, default to empty list like create_user does for mentees
        if users is None:
            users = []
        payload["users"] = [resolve_item_or_id(u) for u in users]

        # Optional fields
        if email is not None:
            payload["email"] = email
        if type_ is not None:
            payload["type"] = type_.value
        if classes is not None:
            payload["classes"] = [resolve_item_or_id(c) for c in classes]
        if description is not None:
            payload["description"] = description

        response = self.post("/api/core/management/classes/", payload)
        return Class.from_dict(response, hive_client=self)

    def delete_class(self, class_: "ClassLike") -> None:
        self.delete(f"/api/core/management/classes/{resolve_item_or_id(class_)}/")
