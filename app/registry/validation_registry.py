"""ValidationRegistry — selects a ValidationProcessor from the ``processor`` strategy."""

from __future__ import annotations

from typing import Any

from app.registry.base import Registry, extract_configuration
from app.registry.implementations.base import ValidationProcessor
from app.registry.implementations.validation import (
    BilingualValidationProcessor,
    StandardValidationProcessor,
)


class ValidationRegistry(Registry[ValidationProcessor]):
    """Maps the ``processor`` strategy value (default ``standard``) to a processor."""

    DISCRIMINATOR = "processor"
    DEFAULT = "standard"

    def resolve(self, profile: Any, **context: Any) -> ValidationProcessor:
        cfg = extract_configuration(profile)
        key = str(cfg.get(self.DISCRIMINATOR, self.DEFAULT)).lower()
        return self.create(key, configuration=cfg, **context)


validation_registry = ValidationRegistry("ValidationRegistry")
validation_registry.register("standard", StandardValidationProcessor)
# 'bilingual' is a business strategy (enforce multiple official languages),
# not an authority — resolved generically, never branched on in code.
validation_registry.register("bilingual", BilingualValidationProcessor)
