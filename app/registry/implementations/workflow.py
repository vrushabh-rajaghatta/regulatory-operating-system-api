"""Workflow processors. Selected by the ``processor`` business strategy."""

from __future__ import annotations

from typing import Any, List, Optional

from app.registry.implementations.base import WorkflowProcessor


class StandardWorkflowProcessor(WorkflowProcessor):
    """Linear state machine driven by the configured ``states`` list."""

    DEFAULT_STATES = ["Draft", "Review", "Approved"]

    @property
    def states(self) -> List[str]:
        return list(self.configuration.get("states") or self.DEFAULT_STATES)

    def next_state(self, current: str) -> Optional[str]:
        states = self.states
        if current not in states:
            raise ValueError(f"Unknown state: {current!r}")
        idx = states.index(current)
        return states[idx + 1] if idx + 1 < len(states) else None


class MedicalWorkflowProcessor(StandardWorkflowProcessor):
    """Medical-device review: dual approval is always enforced."""

    @property
    def requires_dual_approval(self) -> bool:
        return True

    def requires_medical_review(self) -> bool:
        return any("medical" in state.lower() for state in self.states)
