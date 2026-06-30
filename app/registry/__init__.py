"""
Registry layer — maps business configuration to executable application code.

The chain:

    Submission -> Submission Profile -> Configuration Profile -> Registry -> Implementation

The database stores business configuration only (e.g. ``{"package": "zip"}``,
``{"steps": [...]}``); the key→implementation mapping lives here, in code.
Implementations (under ``app.registry.implementations``) are pure and
DB-independent. New implementations are added by writing a class and registering
it — no business entity changes required.

Importing this package registers all default implementations.
"""

from app.registry.base import (
    ConfigurationKeyError,
    ConfigurationProfileLike,
    Registry,
    RegistryError,
    UnknownImplementationError,
    extract_configuration,
)
from app.registry.export_registry import ExportRegistry, export_registry
from app.registry.workflow_registry import WorkflowRegistry, workflow_registry
from app.registry.validation_registry import ValidationRegistry, validation_registry
from app.registry.ai_pipeline_registry import (
    AIPipelineRegistry,
    ai_pipeline_registry,
)
from app.registry.implementations.base import (
    AIPipelineProcessor,
    ExportProcessor,
    Processor,
    ValidationProcessor,
    WorkflowProcessor,
)
from app.registry.runtime import (
    RuntimeImplementations,
    build_runtime_implementations,
)

__all__ = [
    # base
    "Registry",
    "RegistryError",
    "UnknownImplementationError",
    "ConfigurationKeyError",
    "ConfigurationProfileLike",
    "extract_configuration",
    # common processor interfaces
    "Processor",
    "ExportProcessor",
    "WorkflowProcessor",
    "ValidationProcessor",
    "AIPipelineProcessor",
    # registries (classes + singletons)
    "ExportRegistry",
    "export_registry",
    "WorkflowRegistry",
    "workflow_registry",
    "ValidationRegistry",
    "validation_registry",
    "AIPipelineRegistry",
    "ai_pipeline_registry",
    # runtime assembly
    "RuntimeImplementations",
    "build_runtime_implementations",
]
