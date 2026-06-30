"""
A tiny thread-safe in-memory cache for resolved, immutable configuration.

Deliberately dependency-free (no model/service imports) so it can be shared by
both the resolver and the mutating services that need to invalidate it, without
creating import cycles.

Resolved configuration snapshots are immutable and fully detached from any ORM
session, so they are safe to cache process-wide and hand back across requests.
Any admin edit to a configuration profile, submission profile or template
version should ``clear()`` the cache (the registry treats configuration as
immutable, so edits are rare).
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Optional


class _ConfigurationCache:
    def __init__(self) -> None:
        self._store: Dict[Any, Any] = {}
        self._lock = threading.RLock()

    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            return self._store.get(key)

    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            self._store[key] = value

    def invalidate(self, key: Any) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Process-wide singleton.
configuration_cache = _ConfigurationCache()
