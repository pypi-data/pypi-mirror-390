"""
Program resource mixin for HiveClient.

Provides methods for listing and retrieving Program records via the Hive API.
Designed to be mixed into the main HiveClient only.
"""

from typing import Iterable, Optional

from ..src.types.program import Program
from .client_shared import ClientCoreMixin


class ProgramClientMixin(ClientCoreMixin):
    """
    Mixin class adding program-related API methods to the HiveClient.

    Methods
    -------
    get_programs(id__in=None, program_name=None)
        List all or filtered programs via the Hive API.
    get_program(program_id)
        Retrieve a single program record by its id.
    """

    def get_programs(
        self,
        id__in: Optional[list[int]] = None,
        program_name: Optional[str] = None,
    ) -> Iterable[Program]:
        """Yield ``Program`` objects, optionally filtered by ids/name."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        programs: Iterable[Program] = self._get_core_items(
            "/api/core/course/programs/",
            Program,
            id__in=id__in,
        )
        if program_name is not None:
            programs = list(filter(lambda p: p.name == program_name, programs))
        return programs

    def get_program(self, program_id: int) -> Program:
        """Return a single ``Program`` by its id."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"
        return Program.from_dict(
            self.get(f"/api/core/course/programs/{program_id}/"),
            hive_client=self,
        )
