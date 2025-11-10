"""Queues mixin for HiveClient.

Provides retrieval of queue records.
"""

from ..src.types.queue import Queue
from .client_shared import ClientCoreMixin


class QueuesClientMixin(ClientCoreMixin):
    """Mixin that exposes queue retrieval endpoints."""

    def get_queue(self, queue_id: int) -> Queue:
        """Return a single queue by ``queue_id``."""
        from ..client import HiveClient

        assert isinstance(self, HiveClient), "self must be an instance of HiveClient"
        return Queue.from_dict(
            self.get(f"/api/core/queues/{queue_id}/"),
            hive_client=self,
        )
