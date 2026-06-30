"""WorkflowRegistry — selects a WorkflowProcessor from the ``processor`` strategy."""

from __future__ import annotations

from typing import Any

from app.registry.base import Registry, extract_configuration
from app.registry.implementations.base import WorkflowProcessor
from app.registry.implementations.workflow import (
    MedicalWorkflowProcessor,
    StandardWorkflowProcessor,
)


class WorkflowRegistry(Registry[WorkflowProcessor]):
    """Maps the ``processor`` strategy value (default ``standard``) to a processor."""

    DISCRIMINATOR = "processor"
    DEFAULT = "standard"

    def resolve(self, profile: Any, **context: Any) -> WorkflowProcessor:
        cfg = extract_configuration(profile)
        key = str(cfg.get(self.DISCRIMINATOR, self.DEFAULT)).lower()
        return self.create(key, configuration=cfg, **context)


workflow_registry = WorkflowRegistry("WorkflowRegistry")
workflow_registry.register("standard", StandardWorkflowProcessor)
workflow_registry.register("medical", MedicalWorkflowProcessor)
