"""
Registry base.

A registry maps a *business key* found in a ConfigurationProfile's JSON
(e.g. ``"zip"``, ``"DocumentClassification"``, ``"requiredDocuments"``) to an
*implementation factory* in code. The database therefore never knows about
Python classes, modules or service names — it stores business configuration
only; the key→implementation mapping lives here.

This module (and everything under ``app.registry``) is deliberately
DB-independent: no SQLAlchemy or model imports. Inputs are duck-typed via
``ConfigurationProfileLike`` so a registry can accept either the ORM
``ConfigurationProfile``, the resolver's ``ConfigurationProfileView`` or a plain
mapping — without importing any of them.
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")


@runtime_checkable
class ConfigurationProfileLike(Protocol):
    """Anything carrying a business ``configuration`` payload."""

    code: str
    name: str
    configuration: Mapping[str, Any]


class RegistryError(Exception):
    """Base class for registry errors."""


class UnknownImplementationError(RegistryError):
    """Raised when no implementation is registered for a configuration key."""


class ConfigurationKeyError(RegistryError):
    """Raised when a required discriminator is absent from the configuration."""


def extract_configuration(profile: Any) -> Mapping[str, Any]:
    """
    Return the business configuration mapping from a profile-like object.

    Accepts a ``ConfigurationProfileLike`` (ORM model or resolver view) or a raw
    mapping; returns an empty mapping for ``None``.
    """
    if profile is None:
        return {}
    if isinstance(profile, Mapping):
        return profile
    cfg = getattr(profile, "configuration", None)
    return cfg if cfg is not None else {}


class Registry(Generic[T]):
    """
    Maps business keys to implementation factories.

    A *factory* is any callable returning an implementation; typically the
    implementation class itself. Factories are invoked with keyword arguments
    only — ``configuration`` plus any injected dependencies (``**context``) — so
    new dependencies can be threaded through without changing signatures.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._factories: Dict[str, Callable[..., T]] = {}

    def register(
        self, key: str, factory: Optional[Callable[..., T]] = None
    ) -> Callable[..., T]:
        """
        Register an implementation for ``key``. Usable directly::

            registry.register("zip", ZipPackageExporter)

        or as a decorator::

            @registry.register("zip")
            class ZipPackageExporter(Exporter): ...
        """

        def _decorator(f: Callable[..., T]) -> Callable[..., T]:
            self._factories[key] = f
            return f

        return _decorator(factory) if factory is not None else _decorator

    def unregister(self, key: str) -> None:
        self._factories.pop(key, None)

    def is_registered(self, key: str) -> bool:
        return key in self._factories

    def keys(self) -> List[str]:
        """Registered keys in registration order."""
        return list(self._factories.keys())

    def available(self) -> List[str]:
        """Registered keys, sorted (for error messages / introspection)."""
        return sorted(self._factories)

    def create(self, key: str, **context: Any) -> T:
        """Instantiate the implementation registered for ``key`` (DI via context)."""
        factory = self._factories.get(key)
        if factory is None:
            raise UnknownImplementationError(
                f"{self.name}: no implementation registered for '{key}'. "
                f"Available: {', '.join(self.available()) or '(none)'}"
            )
        return factory(**context)
