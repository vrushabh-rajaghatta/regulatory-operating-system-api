"""
ConfigurationResolver — the single source of truth for a submission's runtime
configuration.

Given a Submission ID it loads, in a single eager-loaded query:

    Submission
      └─ Submission Profile
           ├─ Export Profile          (ConfigurationProfile)
           ├─ Workflow Profile        (ConfigurationProfile)
           ├─ Validation Profile      (ConfigurationProfile)
           └─ AI Pipeline Profile     (ConfigurationProfile)
      └─ Template Version

and returns a strongly typed, immutable ``SubmissionRuntimeConfiguration``.

Design goals:
- **Eager load relationships** — one round trip, no lazy-load N+1.
- **Minimize database queries** — a single SELECT resolves the whole graph.
- **Cache immutable configuration** — the returned snapshot is frozen and fully
  detached from the ORM session (plain values + read-only mappings), so it is
  cached process-wide and reused across requests/sessions safely.
- **Single source of truth** — runtime consumers resolve configuration here
  rather than re-querying the profile/template graph ad hoc.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.configuration.cache import configuration_cache
from app.regulatory.models import SubmissionProfile
from app.submissions.models import Submission


def _enum_value(value: Any) -> Optional[str]:
    """Coerce a SQLAlchemy Enum member (or plain string/None) to its string value."""
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def _frozen(mapping: Optional[dict]) -> Mapping[str, Any]:
    """Return a read-only view over a copy of ``mapping`` (never None)."""
    return MappingProxyType(dict(mapping or {}))


class ConfigurationResolutionError(Exception):
    """Base class for configuration resolution errors."""


class SubmissionNotFoundError(ConfigurationResolutionError):
    """Raised when the submission to resolve does not exist."""


# --------------------------------------------------------------------------- #
# Strongly typed, immutable snapshot
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ConfigurationProfileView:
    """Immutable view of a single ConfigurationProfile dimension."""

    id: UUID
    configuration_type_id: UUID
    code: str
    name: str
    version: Optional[str]
    is_active: bool
    configuration: Mapping[str, Any]  # read-only

    def get(self, key: str, default: Any = None) -> Any:
        """Convenience accessor over the business configuration payload."""
        return self.configuration.get(key, default)


@dataclass(frozen=True)
class SubmissionProfileView:
    """Immutable view of the owning SubmissionProfile."""

    id: UUID
    submission_type_id: UUID
    code: str
    name: str
    is_active: bool


@dataclass(frozen=True)
class TemplateVersionView:
    """Immutable view of the governing TemplateVersion."""

    id: UUID
    submission_profile_id: UUID
    version: str
    status: Optional[str]
    is_latest: bool


@dataclass(frozen=True)
class SubmissionRuntimeConfiguration:
    """The fully resolved, immutable runtime configuration for a submission."""

    submission_id: UUID
    sequence_number: str
    status: Optional[str]
    organization_id: UUID
    project_id: UUID
    product_id: UUID
    submission_profile: Optional[SubmissionProfileView]
    export: Optional[ConfigurationProfileView]
    workflow: Optional[ConfigurationProfileView]
    validation: Optional[ConfigurationProfileView]
    ai_pipeline: Optional[ConfigurationProfileView]
    template_version: Optional[TemplateVersionView]

    @property
    def submission_profile_id(self) -> Optional[UUID]:
        return self.submission_profile.id if self.submission_profile else None

    @property
    def template_version_id(self) -> Optional[UUID]:
        return self.template_version.id if self.template_version else None


# --------------------------------------------------------------------------- #
# Resolver
# --------------------------------------------------------------------------- #
class ConfigurationResolver:
    """Resolves (and caches) a submission's runtime configuration."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _cache_key(submission_id: UUID) -> tuple:
        return ("submission_runtime_configuration", str(submission_id))

    def resolve(
        self, submission_id: UUID, *, use_cache: bool = True
    ) -> SubmissionRuntimeConfiguration:
        """
        Resolve the runtime configuration for ``submission_id``.

        Loads the submission, its submission profile, the four configuration
        profiles and the template version in a single eager-loaded query, then
        returns an immutable snapshot. Cached by default (the snapshot is
        session-detached and safe to reuse).
        """
        key = self._cache_key(submission_id)
        if use_cache:
            cached = configuration_cache.get(key)
            if cached is not None:
                return cached

        submission = (
            self.db.query(Submission)
            .options(
                joinedload(Submission.submission_profile).joinedload(
                    SubmissionProfile.export_profile
                ),
                joinedload(Submission.submission_profile).joinedload(
                    SubmissionProfile.workflow_profile
                ),
                joinedload(Submission.submission_profile).joinedload(
                    SubmissionProfile.validation_profile
                ),
                joinedload(Submission.submission_profile).joinedload(
                    SubmissionProfile.ai_pipeline_profile
                ),
                joinedload(Submission.template_version),
            )
            .filter(Submission.id == submission_id)
            .first()
        )
        if submission is None:
            raise SubmissionNotFoundError(f"Submission not found: {submission_id}")

        runtime = self._build(submission)
        if use_cache:
            configuration_cache.set(key, runtime)
        return runtime

    @staticmethod
    def invalidate(submission_id: UUID) -> None:
        """Drop the cached configuration for a single submission."""
        configuration_cache.invalidate(
            ConfigurationResolver._cache_key(submission_id)
        )

    @staticmethod
    def clear_cache() -> None:
        """Drop all cached runtime configuration."""
        configuration_cache.clear()

    # ------------------------------------------------------------------ #
    # Mapping ORM -> immutable views
    # ------------------------------------------------------------------ #
    @staticmethod
    def _profile_view(profile) -> Optional[ConfigurationProfileView]:
        if profile is None:
            return None
        return ConfigurationProfileView(
            id=profile.id,
            configuration_type_id=profile.configuration_type_id,
            code=profile.code,
            name=profile.name,
            version=profile.version,
            is_active=profile.is_active,
            configuration=_frozen(profile.configuration),
        )

    def _build(self, submission: Submission) -> SubmissionRuntimeConfiguration:
        profile = submission.submission_profile
        profile_view = (
            SubmissionProfileView(
                id=profile.id,
                submission_type_id=profile.submission_type_id,
                code=profile.code,
                name=profile.name,
                is_active=profile.is_active,
            )
            if profile is not None
            else None
        )

        tv = submission.template_version
        template_version_view = (
            TemplateVersionView(
                id=tv.id,
                submission_profile_id=tv.submission_profile_id,
                version=tv.version,
                status=_enum_value(tv.status),
                is_latest=tv.is_latest,
            )
            if tv is not None
            else None
        )

        return SubmissionRuntimeConfiguration(
            submission_id=submission.id,
            sequence_number=submission.sequence_number,
            status=_enum_value(submission.status),
            organization_id=submission.organization_id,
            project_id=submission.project_id,
            product_id=submission.product_id,
            submission_profile=profile_view,
            export=self._profile_view(profile.export_profile if profile else None),
            workflow=self._profile_view(profile.workflow_profile if profile else None),
            validation=self._profile_view(profile.validation_profile if profile else None),
            ai_pipeline=self._profile_view(
                profile.ai_pipeline_profile if profile else None
            ),
            template_version=template_version_view,
        )
