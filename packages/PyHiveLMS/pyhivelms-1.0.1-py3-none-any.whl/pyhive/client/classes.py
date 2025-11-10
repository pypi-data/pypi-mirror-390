"""
Class resource mixin for HiveClient.

Provides listing and retrieval of Class records from the Hive API. Use only as a mixin for the main HiveClient.
"""

from typing import Iterable, Optional

from ..src.types.class_ import Class
from ..src.types.enums.class_type_enum import ClassTypeEnum
from .client_shared import ClientCoreMixin


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
