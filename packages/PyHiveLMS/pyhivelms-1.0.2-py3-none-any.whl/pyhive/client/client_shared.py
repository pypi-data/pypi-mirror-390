"""Shared client utilities and common mixin base for Hive API access.

- ``ClientCoreMixin``: base class that provides ``_get_core_items`` used by resource mixins.
"""

from typing import Any, Generator, Iterable, Optional

import httpx

from ..src.authenticated_hive_client import AuthenticatedHiveClient
from .utils import CoreItemTypeT


class ClientCoreMixin(AuthenticatedHiveClient):
    """Common mixin base that exposes ``_get_core_items`` for list endpoints.

    This relies on the authenticated transport provided by the base client and is designed to be used only on
    the composed ``HiveClient``.
    """

    def _get_core_items(
        self,
        endpoint: str,
        item_type: type[CoreItemTypeT],
        /,
        extra_ctor_params: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> Iterable[CoreItemTypeT]:
        """Yield typed items from a list endpoint with optional query parameters.

        Handles both non-paginated list responses and DRF-style paginated
        responses of the form:

            {"count": N, "next": url | null, "previous": url | null, "results": [...]}
        """
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"

        if extra_ctor_params is None:
            extra_ctor_params = {}

        # Build query params, converting lists to comma-separated values
        query_params = httpx.QueryParams()
        for name, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, list):
                query_params = query_params.set(name, ",".join(str(x) for x in value))
            else:
                query_params = query_params.set(name, value)

        data = self.get(endpoint, params=query_params)

        # Non-paginated: assume the payload is the items list (or empty)
        if not (isinstance(data, dict) and "results" in data):
            items: list = data if isinstance(data, list) else []
            yield from (
                item_type.from_dict(x, **extra_ctor_params, hive_client=self)
                for x in items
            )

        # Paginated: follow "next" links and yield all pages
        def _paginate() -> Iterable[CoreItemTypeT]:
            page = data
            while True:
                items = page.get("results", [])
                for x in items:
                    yield item_type.from_dict(x, **extra_ctor_params, hive_client=self)
                next_url = page.get("next")
                if not next_url:
                    break
                page = self.get(next_url)

        return _paginate()
