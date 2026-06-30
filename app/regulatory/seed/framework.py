"""
Core seed framework: the engine shared by every regulatory ecosystem.

Country packages contribute *data only* (master_data, configuration,
submission_profiles, templates, documents, validation); this module contains all
the seeding *logic*. Adding a new country therefore never requires touching this
file — see ``runner.SeedRunner`` for discovery.

Everything here is idempotent: entities are looked up by their natural key and
only created when absent (existing rows are reused, never duplicated).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.regulatory.models import (
    Country,
    Authority,
    Industry,
    Regulation,
    RegulationStatus,
    SubmissionType,
    SubmissionProfile,
    RiskClassification,
    TemplateVersion,
    TemplateStatus,
    TemplateSection,
    RequiredDocument,
    ValidationRule,
    ValidationTargetType,
    ValidationSeverity,
)
from app.configuration.models import ConfigurationType, ConfigurationProfile

SEED_ACTOR = "system-seed"

TEMPLATE_VERSION_LABEL = "2025.1"
TEMPLATE_EFFECTIVE_DATE = date(2025, 1, 1)

# Submission-profile configuration dimensions: (ConfigurationType code, FK field).
DIMENSIONS = (
    ("EXPORT", "export_profile_id"),
    ("WORKFLOW", "workflow_profile_id"),
    ("VALIDATION", "validation_profile_id"),
    ("AI_PIPELINE", "ai_pipeline_profile_id"),
)

_MIME = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "doc": "application/msword",
}


# --------------------------------------------------------------------------- #
# Public builders — imported by country data modules
# --------------------------------------------------------------------------- #
def node(number: str, title: str, order: int, *, required: bool = True,
         description: Optional[str] = None, children: Optional[list] = None) -> dict[str, Any]:
    """Build a template-section spec node (with optional nested children)."""
    return {
        "section_number": number,
        "title": title,
        "order": order,
        "is_required": required,
        "description": description,
        "children": children or [],
    }


def doc(name: str, description: str, *, required: bool = True,
        extensions: tuple[str, ...] = ("pdf",),
        min_files: Optional[int] = None, max_files: Optional[int] = None) -> dict[str, Any]:
    """Build a required-document spec; minimum_files defaults to 1 if mandatory."""
    if min_files is None:
        min_files = 1 if required else 0
    return {
        "name": name,
        "description": description,
        "required": required,
        "allowed_extensions": list(extensions),
        "accepted_mime_types": [_MIME[e] for e in extensions],
        "minimum_files": min_files,
        "maximum_files": max_files,
    }


def doc_rule(document: str, *, conditional: bool = False, min_files: int = 1) -> dict[str, Any]:
    """A 'document required' rule (Error), or a 'when applicable' rule (Warning)."""
    if conditional:
        return {
            "target_type": ValidationTargetType.DOCUMENT,
            "target_reference": document,
            "rule_type": "document_conditional",
            "rule_expression": json.dumps({"op": "document_present", "document": document, "condition": "applicable"}),
            "error_message": f"{document} is required when applicable.",
            "severity": ValidationSeverity.WARNING,
        }
    return {
        "target_type": ValidationTargetType.DOCUMENT,
        "target_reference": document,
        "rule_type": "document_required",
        "rule_expression": json.dumps({"op": "document_present", "document": document, "min_files": min_files}),
        "error_message": f"{document} is mandatory.",
        "severity": ValidationSeverity.ERROR,
    }


def section_rule(number: str, title: str) -> dict[str, Any]:
    """A 'section must be completed' rule (Error)."""
    return {
        "target_type": ValidationTargetType.SECTION,
        "target_reference": number,
        "rule_type": "section_required",
        "rule_expression": json.dumps({"op": "section_complete", "section": number}),
        "error_message": f"Section {number} ({title}) must be completed.",
        "severity": ValidationSeverity.ERROR,
    }


# --------------------------------------------------------------------------- #
# Ecosystem descriptor — built by each country package's __init__
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Ecosystem:
    code: str                       # e.g. "CA"
    name: str                       # e.g. "Canada"
    authority_name: str             # e.g. "Health Canada" (for re-seed by authority)
    master_data: dict[str, Any]
    configuration_profiles: dict[str, list[dict[str, Any]]]   # type code -> [profile]
    submission_profiles: dict[str, tuple[str, str, str, str]]  # st_code -> (exp, wf, val, ai)
    structures: dict[str, list[dict[str, Any]]]               # structure_key -> section tree
    profile_structure: dict[str, str]                         # st_code -> structure_key
    release_notes: dict[str, str]                             # structure_key -> note
    required_documents: dict[str, list[dict[str, Any]]]       # structure_key -> [doc]
    validation_rules: dict[str, list[dict[str, Any]]]         # structure_key -> [rule]


# --------------------------------------------------------------------------- #
# Stats + context
# --------------------------------------------------------------------------- #
class Stats:
    """Tracks created vs. reused counts."""

    def __init__(self) -> None:
        self.created = 0
        self.reused = 0

    def record(self, created: bool) -> None:
        if created:
            self.created += 1
        else:
            self.reused += 1

    def merge(self, other: "Stats") -> None:
        self.created += other.created
        self.reused += other.reused


class SeedContext:
    """Wraps the DB session + stats, providing the idempotent get-or-create."""

    def __init__(self, db: Session, stats: Stats):
        self.db = db
        self.stats = stats

    def get_or_create(self, model, *, defaults: Optional[dict[str, Any]] = None, **filters):
        """Return (instance, created). Looks up by filters; creates with filters+defaults if absent."""
        instance = self.db.query(model).filter_by(**filters).first()
        if instance is not None:
            self.stats.record(False)
            return instance, False
        params = {**filters, **(defaults or {})}
        instance = model(**params)
        self.db.add(instance)
        self.db.flush()
        self.stats.record(True)
        return instance, True


# --------------------------------------------------------------------------- #
# Configuration seeding (shared by common + per-country)
# --------------------------------------------------------------------------- #
def seed_configuration_types(ctx: SeedContext, types: list[dict[str, str]]) -> None:
    for spec in types:
        ctx.get_or_create(
            ConfigurationType, code=spec["code"],
            defaults={"name": spec["name"], "description": spec.get("description"),
                      "is_active": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
        )


def seed_configuration_profiles(ctx: SeedContext, profiles_by_type: dict[str, list[dict[str, Any]]]) -> None:
    for type_code, profiles in profiles_by_type.items():
        config_type, _ = ctx.get_or_create(
            ConfigurationType, code=type_code,
            defaults={"name": type_code.replace("_", " ").title(), "is_active": True,
                      "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
        )
        for spec in profiles:
            ctx.get_or_create(
                ConfigurationProfile,
                configuration_type_id=config_type.id,
                code=spec["code"],
                version=spec.get("version", "1.0"),
                defaults={
                    "name": spec["name"],
                    "description": spec.get("description"),
                    "configuration": spec["configuration"],
                    "is_active": True,
                    "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR,
                },
            )


# --------------------------------------------------------------------------- #
# Ecosystem seeder — runs the per-country steps (each independently runnable)
# --------------------------------------------------------------------------- #
class EcosystemSeeder:
    """Seeds a single ecosystem. Steps query what they need, so they are safe to
    run individually (e.g. templates-only)."""

    def __init__(self, ctx: SeedContext, eco: Ecosystem):
        self.ctx = ctx
        self.eco = eco
        self._config_cache: dict[tuple[str, str], Optional[ConfigurationProfile]] = {}

    # -- lookups --------------------------------------------------------- #
    def _country(self) -> Optional[Country]:
        return self.ctx.db.query(Country).filter(Country.code == self.eco.code).first()

    def _submission_type(self, st_code: str) -> Optional[SubmissionType]:
        return (
            self.ctx.db.query(SubmissionType)
            .join(Regulation, SubmissionType.regulation_id == Regulation.id)
            .join(Authority, Regulation.authority_id == Authority.id)
            .join(Country, Authority.country_id == Country.id)
            .filter(Country.code == self.eco.code, SubmissionType.code == st_code)
            .first()
        )

    def _submission_profile(self, st_code: str) -> Optional[SubmissionProfile]:
        st = self._submission_type(st_code)
        if st is None:
            return None
        return (
            self.ctx.db.query(SubmissionProfile)
            .filter(SubmissionProfile.submission_type_id == st.id, SubmissionProfile.code == "DEFAULT")
            .first()
        )

    def _config_profile(self, type_code: str, profile_code: str) -> Optional[ConfigurationProfile]:
        key = (type_code, profile_code)
        if key not in self._config_cache:
            self._config_cache[key] = (
                self.ctx.db.query(ConfigurationProfile)
                .join(ConfigurationType, ConfigurationProfile.configuration_type_id == ConfigurationType.id)
                .filter(ConfigurationType.code == type_code, ConfigurationProfile.code == profile_code)
                .first()
            )
        return self._config_cache[key]

    # -- steps ----------------------------------------------------------- #
    def seed_configuration(self) -> None:
        seed_configuration_profiles(self.ctx, self.eco.configuration_profiles)

    def seed_master_data(self) -> None:
        from app.regulatory.seed.common import INDUSTRIES

        md = self.eco.master_data
        c = md["country"]
        country, _ = self.ctx.get_or_create(
            Country, code=c["code"],
            defaults={"name": c["name"], "is_active": True,
                      "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
        )
        a = md["authority"]
        authority, _ = self.ctx.get_or_create(
            Authority, country_id=country.id, name=a["name"],
            defaults={"abbreviation": a.get("abbreviation"), "website": a.get("website"),
                      "description": a.get("description"), "is_active": True,
                      "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
        )

        rc_map: dict[str, RiskClassification] = {}
        for rc in md.get("risk_classes", []):
            risk_class, _ = self.ctx.get_or_create(
                RiskClassification, code=rc["code"],
                defaults={"name": rc["name"], "sort_order": rc["sort_order"],
                          "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )
            rc_map[rc["code"]] = risk_class

        for reg in md.get("regulations", []):
            ind_spec = INDUSTRIES[reg["industry"]]
            industry, _ = self.ctx.get_or_create(
                Industry, code=reg["industry"],
                defaults={"name": ind_spec["name"], "description": ind_spec["description"],
                          "is_active": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )
            regulation, _ = self.ctx.get_or_create(
                Regulation, authority_id=authority.id, code=reg["code"], version=None,
                defaults={"industry_id": industry.id, "name": reg["name"],
                          "description": reg.get("description"), "status": RegulationStatus.ACTIVE,
                          "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )
            applicable = [rc_map[code] for code in reg.get("risk_class_codes", [])]
            for st in reg.get("submission_types", []):
                submission_type, _ = self.ctx.get_or_create(
                    SubmissionType, regulation_id=regulation.id, code=st["code"],
                    defaults={"name": st["name"], "description": st.get("description"),
                              "sequence_prefix": st.get("sequence_prefix"),
                              "allows_multiple_sequences": st.get("allows_multiple_sequences", False),
                              "is_active": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
                )
                for risk_class in applicable:
                    if risk_class not in submission_type.risk_classifications:
                        submission_type.risk_classifications.append(risk_class)

    def seed_submission_profiles(self) -> None:
        for st_code, mapping in self.eco.submission_profiles.items():
            submission_type = self._submission_type(st_code)
            if submission_type is None:
                continue
            links: dict[str, Any] = {}
            for (type_code, fk_field), profile_code in zip(DIMENSIONS, mapping):
                cp = self._config_profile(type_code, profile_code)
                links[fk_field] = cp.id if cp else None
            self.ctx.get_or_create(
                SubmissionProfile,
                submission_type_id=submission_type.id, code="DEFAULT",
                defaults={"name": f"{submission_type.name} Profile",
                          "description": f"Default submission profile for {submission_type.name}.",
                          "is_active": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR, **links},
            )

    def seed_templates(self) -> None:
        for st_code, structure_key in self.eco.profile_structure.items():
            profile = self._submission_profile(st_code)
            if profile is None:
                continue
            template_version, _ = self.ctx.get_or_create(
                TemplateVersion,
                submission_profile_id=profile.id, version=TEMPLATE_VERSION_LABEL,
                defaults={"effective_date": TEMPLATE_EFFECTIVE_DATE, "status": TemplateStatus.ACTIVE,
                          "release_notes": self.eco.release_notes.get(structure_key, "Initial 2025.1 template release."),
                          "is_latest": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )
            self._seed_sections(template_version, self.eco.structures.get(structure_key, []), parent_id=None)
            self._seed_documents(template_version, self.eco.required_documents.get(structure_key, []))
            self._seed_validation(template_version, self.eco.validation_rules.get(structure_key, []))

    # -- template children ---------------------------------------------- #
    def _seed_sections(self, template_version, sections, *, parent_id) -> None:
        for spec in sections:
            section, _ = self.ctx.get_or_create(
                TemplateSection,
                template_version_id=template_version.id, section_number=spec["section_number"],
                defaults={"parent_id": parent_id, "title": spec["title"],
                          "description": spec.get("description"), "help_text": spec.get("help_text"),
                          "order": spec["order"], "is_required": spec["is_required"],
                          "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )
            if spec.get("children"):
                self._seed_sections(template_version, spec["children"], parent_id=section.id)

    def _seed_documents(self, template_version, docs) -> None:
        for spec in docs:
            self.ctx.get_or_create(
                RequiredDocument,
                template_version_id=template_version.id, name=spec["name"],
                defaults={"description": spec["description"], "required": spec["required"],
                          "allowed_extensions": spec["allowed_extensions"],
                          "accepted_mime_types": spec["accepted_mime_types"],
                          "minimum_files": spec["minimum_files"], "maximum_files": spec["maximum_files"],
                          "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )

    def _seed_validation(self, template_version, rules) -> None:
        for spec in rules:
            self.ctx.get_or_create(
                ValidationRule,
                template_version_id=template_version.id,
                rule_type=spec["rule_type"], target_reference=spec["target_reference"],
                defaults={"target_type": spec["target_type"], "rule_expression": spec["rule_expression"],
                          "error_message": spec["error_message"], "severity": spec["severity"],
                          "is_active": True, "created_by": SEED_ACTOR, "updated_by": SEED_ACTOR},
            )

    # -- orchestration --------------------------------------------------- #
    def seed_all(self) -> None:
        self.seed_master_data()
        self.seed_configuration()
        self.seed_submission_profiles()
        self.seed_templates()
