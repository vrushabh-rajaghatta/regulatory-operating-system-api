"""
Common processor interfaces.

Four interfaces — one per dimension — that every implementation implements:

    ExportProcessor, WorkflowProcessor, ValidationProcessor, AIPipelineProcessor

All are pure and DB-independent: a processor is constructed from a business
``configuration`` mapping plus any injected dependencies (``**context``), and
knows nothing about where the configuration came from.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional


class Processor(ABC):
    """Shared base — every processor is built from business configuration + DI context."""

    def __init__(self, configuration: Mapping[str, Any], **context: Any) -> None:
        self.configuration = configuration
        self.context = context  # injected dependencies (logger, clients, ...)

    def describe(self) -> Dict[str, Any]:
        return {"processor": type(self).__name__, "configuration": dict(self.configuration)}

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"


class ExportProcessor(Processor):
    """Packages a submission for transport."""

    package_format: str = "generic"

    @property
    def compression(self) -> bool:
        return bool(self.configuration.get("compression", False))

    @property
    def manifest_version(self) -> Any:
        return self.configuration.get("manifestVersion")

    def _descriptor(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "package_format": self.package_format,
            "compression": self.compression,
            "manifest_version": self.manifest_version,
            "documents": list(payload.get("documents", [])),
        }

    @abstractmethod
    def export(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Produce a package descriptor for ``payload``."""


class WorkflowProcessor(Processor):
    """Drives a submission through its review states."""

    @property
    def states(self) -> List[str]:
        return list(self.configuration.get("states", []))

    @property
    def requires_dual_approval(self) -> bool:
        return bool(self.configuration.get("requiresDualApproval", False))

    def initial_state(self) -> Optional[str]:
        return self.states[0] if self.states else None

    def terminal_state(self) -> Optional[str]:
        return self.states[-1] if self.states else None

    @abstractmethod
    def next_state(self, current: str) -> Optional[str]:
        """Return the state that follows ``current`` (or None at the end)."""


class ValidationProcessor(Processor):
    """Validates a submission ``target`` against the configured rules."""

    @property
    def block_on_error(self) -> bool:
        return bool(self.configuration.get("blockOnError", False))

    def _report(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        has_error = any(i.get("severity") == "Error" for i in issues)
        return {
            "issues": issues,
            "passed": not has_error,
            "block_on_error": self.block_on_error,
        }

    @abstractmethod
    def validate(self, target: Mapping[str, Any]) -> Dict[str, Any]:
        """Return a report ``{issues, passed, block_on_error}``."""


class AIPipelineProcessor(Processor):
    """Runs an ordered chain of AI steps over a payload."""

    @property
    def languages(self) -> List[str]:
        return list(self.configuration.get("languages", []))

    @property
    def minimum_confidence(self) -> Optional[float]:
        value = self.configuration.get("minimumConfidence")
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @abstractmethod
    def steps(self) -> List[str]:
        """The ordered step names this pipeline will run."""

    @abstractmethod
    def run(self, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Execute the steps over ``payload`` and return the result."""
