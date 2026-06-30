"""
Regulatory Engine models.

Master/reference entities for the regulatory domain. These are global
(not organization-scoped) and form the backbone of regulatory intelligence:

    Country 1---* Authority 1---* Regulation *---1 Industry
"""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, Enum, ForeignKey, Date, Table, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.models import BaseModel, AuditMixin


# Association table mapping submission types to the risk classifications they support.
# A submission type can support multiple risk classes, and a risk class can apply to
# multiple submission types (many-to-many).
submission_type_risk_class = Table(
    "submission_type_risk_class",
    BaseModel.metadata,
    Column(
        "submission_type_id",
        UUID(as_uuid=True),
        ForeignKey("submission_types.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "risk_classification_id",
        UUID(as_uuid=True),
        ForeignKey("risk_classifications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class RegulationStatus(str, enum.Enum):
    """Lifecycle status of a regulation."""
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"


class TemplateStatus(str, enum.Enum):
    """Lifecycle status of a template version."""
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"


class ValidationTargetType(str, enum.Enum):
    """What a validation rule is evaluated against."""
    DOCUMENT = "Document"
    SECTION = "Section"
    SUBMISSION = "Submission"


class ValidationSeverity(str, enum.Enum):
    """Severity of a validation rule violation."""
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"


class Country(BaseModel, AuditMixin):
    """
    A regulatory jurisdiction identified by its ISO code.

    Parent of one or more regulatory authorities.
    """

    __tablename__ = "countries"

    code = Column(String(10), nullable=False, unique=True, index=True)  # ISO code, e.g. "US", "CA"
    name = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    authorities = relationship(
        "Authority",
        back_populates="country",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Country(id={self.id}, code='{self.code}', name='{self.name}')>"


class Authority(BaseModel, AuditMixin):
    """
    A regulatory authority (e.g. FDA, EMA, Health Canada) within a country.
    """

    __tablename__ = "authorities"
    __table_args__ = (
        UniqueConstraint("country_id", "name", name="uq_authorities_country_id_name"),
    )

    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    abbreviation = Column(String(50), nullable=True, index=True)
    website = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    country = relationship("Country", back_populates="authorities")
    regulations = relationship(
        "Regulation",
        back_populates="authority",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Authority(id={self.id}, name='{self.name}', country={self.country_id})>"


class Industry(BaseModel, AuditMixin):
    """
    An industry vertical the platform regulates (e.g. Pharmaceutical,
    Medical Device, In-Vitro Diagnostics).
    """

    __tablename__ = "industries"

    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    regulations = relationship(
        "Regulation",
        back_populates="industry",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Industry(id={self.id}, code='{self.code}', name='{self.name}')>"


class Regulation(BaseModel, AuditMixin):
    """
    A regulation issued by an authority and scoped to an industry.

    Tracks effective/expiry dates, version and lifecycle status.
    """

    __tablename__ = "regulations"
    __table_args__ = (
        UniqueConstraint("authority_id", "code", "version", name="uq_regulations_authority_code_version"),
    )

    authority_id = Column(UUID(as_uuid=True), ForeignKey("authorities.id"), nullable=False, index=True)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    version = Column(String(50), nullable=True)
    status = Column(Enum(RegulationStatus), default=RegulationStatus.DRAFT, nullable=False, index=True)

    # Relationships
    authority = relationship("Authority", back_populates="regulations")
    industry = relationship("Industry", back_populates="regulations")
    submission_types = relationship(
        "SubmissionType",
        back_populates="regulation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Regulation(id={self.id}, code='{self.code}', status='{self.status}')>"


class SubmissionType(BaseModel, AuditMixin):
    """
    A type of submission permitted under a regulation
    (e.g. "New Drug Application", "Amendment", "Annual Report").

    Drives the sequence-numbering behaviour for submissions created against it.
    """

    __tablename__ = "submission_types"
    __table_args__ = (
        UniqueConstraint("regulation_id", "code", name="uq_submission_types_regulation_id_code"),
    )

    regulation_id = Column(UUID(as_uuid=True), ForeignKey("regulations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sequence_prefix = Column(String(50), nullable=True)
    allows_multiple_sequences = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    regulation = relationship("Regulation", back_populates="submission_types")
    risk_classifications = relationship(
        "RiskClassification",
        secondary=submission_type_risk_class,
        back_populates="submission_types",
    )
    submission_profiles = relationship(
        "SubmissionProfile",
        back_populates="submission_type",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SubmissionType(id={self.id}, code='{self.code}', regulation={self.regulation_id})>"


class SubmissionProfile(BaseModel, AuditMixin):
    """
    Configuration that rarely changes between template versions, for a
    submission type. Sits between SubmissionType and TemplateVersion in the
    regulatory hierarchy.

    Strategy configuration is no longer stored inline. Each dimension — export,
    workflow, validation and AI pipeline — references a reusable
    ``ConfigurationProfile`` in the Configuration Registry. Section definitions
    still live on TemplateVersion via TemplateSection.
    """

    __tablename__ = "submission_profiles"
    __table_args__ = (
        UniqueConstraint("submission_type_id", "code", name="uq_submission_profiles_type_code"),
    )

    submission_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submission_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Configuration Registry references. Nullable for backwards compatibility;
    # SET NULL so deleting a configuration profile never deletes the submission
    # profile that referenced it.
    export_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("configuration_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    workflow_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("configuration_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    validation_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("configuration_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ai_pipeline_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("configuration_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    submission_type = relationship("SubmissionType", back_populates="submission_profiles")
    export_profile = relationship(
        "ConfigurationProfile", foreign_keys=[export_profile_id]
    )
    workflow_profile = relationship(
        "ConfigurationProfile", foreign_keys=[workflow_profile_id]
    )
    validation_profile = relationship(
        "ConfigurationProfile", foreign_keys=[validation_profile_id]
    )
    ai_pipeline_profile = relationship(
        "ConfigurationProfile", foreign_keys=[ai_pipeline_profile_id]
    )
    template_versions = relationship(
        "TemplateVersion",
        back_populates="submission_profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<SubmissionProfile(id={self.id}, code='{self.code}', "
            f"submission_type={self.submission_type_id})>"
        )


class RiskClassification(BaseModel, AuditMixin):
    """
    A generic risk classification (e.g. a device/product risk class).

    Deliberately not tied to any specific scheme or hardcoded set of classes —
    classes are data, configured per the regulatory context.
    """

    __tablename__ = "risk_classifications"

    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False, index=True)

    # Relationships
    submission_types = relationship(
        "SubmissionType",
        secondary=submission_type_risk_class,
        back_populates="risk_classifications",
    )

    def __repr__(self) -> str:
        return f"<RiskClassification(id={self.id}, code='{self.code}', name='{self.name}')>"


class TemplateVersion(BaseModel, AuditMixin):
    """
    Versioned regulatory content for a submission profile.

    Belongs to a SubmissionProfile (which in turn belongs to a SubmissionType).
    Holds only versioned content/lifecycle metadata — the configuration that
    rarely changes lives on the SubmissionProfile. `is_latest` is scoped per
    submission profile.
    """

    __tablename__ = "template_versions"
    __table_args__ = (
        UniqueConstraint(
            "submission_profile_id",
            "version",
            name="uq_template_versions_profile_version",
        ),
    )

    submission_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submission_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(50), nullable=False, index=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    release_notes = Column(Text, nullable=True)
    status = Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT, nullable=False, index=True)
    is_latest = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    submission_profile = relationship("SubmissionProfile", back_populates="template_versions")
    sections = relationship(
        "TemplateSection",
        back_populates="template_version",
        cascade="all, delete-orphan",
    )
    required_documents = relationship(
        "RequiredDocument",
        back_populates="template_version",
        cascade="all, delete-orphan",
    )
    validation_rules = relationship(
        "ValidationRule",
        back_populates="template_version",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TemplateVersion(id={self.id}, version='{self.version}', "
            f"submission_profile={self.submission_profile_id})>"
        )


class RequiredDocument(BaseModel, AuditMixin):
    """
    A document that a template version requires (or optionally accepts).

    Defines the upload constraints — allowed file extensions, accepted MIME
    types and the permitted number of files — used to validate and to scaffold
    placeholder document slots when a submission is created.
    """

    __tablename__ = "required_documents"
    __table_args__ = (
        UniqueConstraint(
            "template_version_id", "name", name="uq_required_documents_version_name"
        ),
    )

    template_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=True, nullable=False, index=True)
    allowed_extensions = Column(JSONB, nullable=True)  # e.g. ["pdf", "docx"]
    accepted_mime_types = Column(JSONB, nullable=True)  # e.g. ["application/pdf"]
    minimum_files = Column(Integer, default=0, nullable=False)
    maximum_files = Column(Integer, nullable=True)  # null = unlimited

    # Relationships
    template_version = relationship("TemplateVersion", back_populates="required_documents")
    section_rules = relationship(
        "SectionRule",
        back_populates="required_document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<RequiredDocument(id={self.id}, name='{self.name}', "
            f"template_version={self.template_version_id})>"
        )


class ValidationRule(BaseModel, AuditMixin):
    """
    A database-driven validation rule scoped to a template version.

    Describes *what* should be validated (target, rule type, expression) and
    *how to report it* (message, severity) — but carries no execution logic.
    A separate engine (not implemented here) is expected to interpret these
    rows at validation time.
    """

    __tablename__ = "validation_rules"

    template_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type = Column(Enum(ValidationTargetType), nullable=False, index=True)
    # Free-form reference to the concrete target (e.g. a section number or document
    # name) within the chosen target_type. Null for submission-wide rules.
    target_reference = Column(String(255), nullable=True, index=True)
    rule_type = Column(String(100), nullable=False, index=True)  # e.g. "required", "regex"
    rule_expression = Column(Text, nullable=True)  # interpreted by the (future) engine
    error_message = Column(Text, nullable=True)
    severity = Column(Enum(ValidationSeverity), default=ValidationSeverity.ERROR, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    template_version = relationship("TemplateVersion", back_populates="validation_rules")

    def __repr__(self) -> str:
        return (
            f"<ValidationRule(id={self.id}, target_type='{self.target_type}', "
            f"rule_type='{self.rule_type}', template_version={self.template_version_id})>"
        )


class SectionRule(BaseModel, AuditMixin):
    """
    Links a template section to a required document.

    A section can have many SectionRules (and thus map to one or more required
    documents); each row also carries a ``rule_type`` and a
    ``confidence_threshold`` for a future AI matching engine to consume. No AI
    logic is implemented here — these are configuration rows only.
    """

    __tablename__ = "section_rules"
    __table_args__ = (
        UniqueConstraint(
            "template_section_id",
            "required_document_id",
            "rule_type",
            name="uq_section_rules_section_document_rule_type",
        ),
    )

    template_section_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    required_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("required_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_type = Column(String(100), nullable=False, index=True)
    confidence_threshold = Column(Float, nullable=True)  # e.g. 0.0–1.0, consumed by future engine

    # Relationships
    template_section = relationship("TemplateSection", back_populates="section_rules")
    required_document = relationship("RequiredDocument", back_populates="section_rules")

    def __repr__(self) -> str:
        return (
            f"<SectionRule(id={self.id}, section={self.template_section_id}, "
            f"document={self.required_document_id}, rule_type='{self.rule_type}')>"
        )


class TemplateSection(BaseModel, AuditMixin):
    """
    A section within a template version, forming a hierarchical structure.

    Sections belong to a single ``TemplateVersion`` and may nest arbitrarily
    via ``parent_id`` (a self-reference). This is the template blueprint that
    drives dossier structure — distinct from ``DossierSection``, which holds a
    submission's actual per-section content.
    """

    __tablename__ = "template_sections"
    __table_args__ = (
        UniqueConstraint(
            "template_version_id",
            "section_number",
            name="uq_template_sections_version_section_number",
        ),
    )

    template_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("template_sections.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    section_number = Column(String(50), nullable=False, index=True)  # e.g. "1", "1.1", "2.3.4"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False, index=True)
    help_text = Column(Text, nullable=True)

    # Relationships
    template_version = relationship("TemplateVersion", back_populates="sections")
    parent = relationship(
        "TemplateSection",
        remote_side="TemplateSection.id",
        back_populates="children",
    )
    children = relationship(
        "TemplateSection",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="TemplateSection.order",
    )
    section_rules = relationship(
        "SectionRule",
        back_populates="template_section",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TemplateSection(id={self.id}, section_number='{self.section_number}', "
            f"template_version={self.template_version_id})>"
        )
