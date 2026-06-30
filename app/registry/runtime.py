"""
Runtime assembly: ConfigurationProfiles -> implementation objects.

This is the join point of the chain

    Submission -> Submission Profile -> Configuration Profile -> Registry -> Implementation

``build_runtime_implementations`` accepts profile-like objects (the ORM
``ConfigurationProfile`` or the resolver's ``ConfigurationProfileView`` — both
satisfy ``ConfigurationProfileLike``) and returns the four resolved
implementations. It stays DB-independent: it never imports models or the
resolver, only duck-typed configuration carriers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.registry.ai_pipeline_registry import ai_pipeline_registry
from app.registry.export_registry import export_registry
from app.registry.implementations.base import (
    AIPipelineProcessor,
    ExportProcessor,
    ValidationProcessor,
    WorkflowProcessor,
)
from app.registry.validation_registry import validation_registry
from app.registry.workflow_registry import workflow_registry


@dataclass(frozen=True)
class RuntimeImplementations:
    """The four resolved processors for a submission's runtime."""

    export: Optional[ExportProcessor]
    workflow: Optional[WorkflowProcessor]
    validation: Optional[ValidationProcessor]
    ai_pipeline: Optional[AIPipelineProcessor]


def build_runtime_implementations(
    *,
    export: Any = None,
    workflow: Any = None,
    validation: Any = None,
    ai_pipeline: Any = None,
    **context: Any,
) -> RuntimeImplementations:
    """
    Resolve each provided ConfigurationProfile to its implementation.

    Pass the resolver's views, e.g.::

        runtime = ConfigurationResolver(db).resolve(submission_id)
        impls = build_runtime_implementations(
            export=runtime.export,
            workflow=runtime.workflow,
            validation=runtime.validation,
            ai_pipeline=runtime.ai_pipeline,
        )

    A ``None`` dimension resolves to ``None``. Extra keyword arguments are
    injected into every implementation (dependency injection).
    """
    return RuntimeImplementations(
        export=export_registry.resolve(export, **context) if export is not None else None,
        workflow=workflow_registry.resolve(workflow, **context)
        if workflow is not None
        else None,
        validation=validation_registry.resolve(validation, **context)
        if validation is not None
        else None,
        ai_pipeline=ai_pipeline_registry.resolve(ai_pipeline, **context)
        if ai_pipeline is not None
        else None,
    )
