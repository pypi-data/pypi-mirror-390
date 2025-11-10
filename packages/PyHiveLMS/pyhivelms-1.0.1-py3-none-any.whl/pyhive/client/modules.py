"""
Module resource mixin for HiveClient.

Adds methods for listing and retrieving Module records via the Hive API. Intended for use
as a mixin on the main HiveClient only.
"""

from typing import TYPE_CHECKING, Iterable, Optional

from ..src.types.module import Module
from .client_shared import ClientCoreMixin
from .utils import resolve_item_or_id

if TYPE_CHECKING:
    from ..src.types.program import ProgramLike
    from ..src.types.subject import SubjectLike

class ModuleClientMixin(ClientCoreMixin):
    """
    Mixin class providing module-related API methods for HiveClient.

    Methods
    -------
    get_modules(parent_subject__id=None, parent_subject=None, module_name=None, ...)
        List all or filtered modules; supports filtering by subject and parent program.
    get_module(module_id)
        Retrieve a single module record by id.
    """

    def get_modules(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        /,
        parent_subject__id: Optional[int] = None,
        parent_subject__parent_program__id__in: Optional[list[int]] = None,
        # Non built-in filters
        parent_subject: Optional["SubjectLike"] = None,
        parent_program: Optional["ProgramLike"] = None,
        module_name: Optional[str] = None,
    ) -> Iterable[Module]:
        """Yield ``Module`` objects, supporting filtering by subject and program."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        assert (
            not (
                parent_subject__parent_program__id__in is not None
                and parent_program is not None
            )
        ) or (
            len(parent_subject__parent_program__id__in) == 1
            and parent_subject__parent_program__id__in[0]
            == resolve_item_or_id(parent_program)
        ), "parent_subject__parent_program__id__in and parent_program filters conflict!"

        if parent_program:
            parent_subject__parent_program__id__in = [
                resolve_item_or_id(parent_program)
            ]

        modules: Iterable[Module] = self._get_core_items(
            "/api/core/course/modules/",
            Module,
            parent_subject__parent_program__id__in=parent_subject__parent_program__id__in,
            parent_subject__id=(
                parent_subject__id
                if parent_subject__id is not None
                else resolve_item_or_id(parent_subject)
            ),
        )
        if module_name is not None:
            modules = filter(lambda m: m.name == module_name, modules)
        return modules

    def get_module(self, module_id: int) -> Module:
        """Return a single ``Module`` by its id."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        return Module.from_dict(
            self.get(f"/api/core/course/modules/{module_id}/"),
            hive_client=self,
        )
