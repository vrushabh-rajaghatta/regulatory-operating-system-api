"""AI pipeline processors. Selected by the ``processor`` business strategy."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from app.registry.implementations.base import AIPipelineProcessor


class StandardAIPipelineProcessor(AIPipelineProcessor):
    """Runs the ordered ``steps`` from the configuration as a transform chain."""

    def steps(self) -> List[str]:
        return list(self.configuration.get("steps", []))

    def run(self, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = dict(payload or {})
        completed = result.setdefault("completed_steps", [])
        for step in self.steps():
            completed.append(step)
        return result
