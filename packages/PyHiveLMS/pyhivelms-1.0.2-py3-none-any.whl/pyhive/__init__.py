"""Public package for the pyhive distribution.

Expose the public convenience symbol `HiveClient` at package level so users
can do `from pyhive import HiveClient`.
"""

from __future__ import annotations

# Import the implementation from the `pyhive` package (implementation
# lives there) and expose the client at package level.
from pyhive.client import HiveClient  # re-export

__all__ = ["HiveClient"]
