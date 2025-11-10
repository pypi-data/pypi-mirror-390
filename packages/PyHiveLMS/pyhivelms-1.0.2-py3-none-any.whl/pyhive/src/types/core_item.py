"""Base class for Hive core items."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from ...client import HiveClient


class HiveCoreItem:
    """Base class for Hive core items."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize this HiveCoreItem instance to a plain dictionary."""
        raise NotImplementedError

    @classmethod
    def from_dict(
        cls, src_dict: Mapping[str, Any], hive_client: "HiveClient"
    ) -> Self:  # noqa: D102
        """Deserialize a HiveCoreItem instance from a mapping."""
        raise NotImplementedError
