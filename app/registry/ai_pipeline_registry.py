"""AIPipelineRegistry — selects an AIPipelineProcessor from the ``processor`` strategy."""

from __future__ import annotations

from typing import Any

from app.registry.base import Registry, extract_configuration
from app.registry.implementations.base import AIPipelineProcessor
from app.registry.implementations.ai_pipeline import StandardAIPipelineProcessor


class AIPipelineRegistry(Registry[AIPipelineProcessor]):
    """Maps the ``processor`` strategy value (default ``standard``) to a processor."""

    DISCRIMINATOR = "processor"
    DEFAULT = "standard"

    def resolve(self, profile: Any, **context: Any) -> AIPipelineProcessor:
        cfg = extract_configuration(profile)
        key = str(cfg.get(self.DISCRIMINATOR, self.DEFAULT)).lower()
        return self.create(key, configuration=cfg, **context)


ai_pipeline_registry = AIPipelineRegistry("AIPipelineRegistry")
ai_pipeline_registry.register("standard", StandardAIPipelineProcessor)
