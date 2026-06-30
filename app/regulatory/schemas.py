"""
Regulatory Engine schemas for API request/response validation.
"""

from pydantic import Field, ConfigDict, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
import enum

from app.core.schemas import BaseSchema, TimestampSchema, UUIDSchema
from app.configuration.schemas import ConfigurationProfileSummary


# Mirror of app.regulatory.models.RegulationStatus for the API layer.
class RegulationStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"


# Mirror of app.regulatory.models.TemplateStatus for the API layer.
class TemplateStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"


# Mirror of app.regulatory.models.ValidationTargetType for the API layer.
class ValidationTargetTypeEnum(str, enum.Enum):
    DOCUMENT = "Document"
    SECTION = "Section"
    SUBMISSION = "Submission"


# Mirror of app.regulatory.models.ValidationSeverity for the API layer.
class ValidationSeverityEnum(str, enum.Enum):
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"


# --------------------------------------------------------------------------- #
# Country
# --------------------------------------------------------------------------- #
class CountryBase(BaseSchema):
    """Base country schema with common fields."""

    code: str = Field(..., min_length=2, max_length=10, description="ISO country code, e.g. 'US'")
    name: str = Field(..., min_length=1, max_length=255, description="Country name")
    is_active: bool = Field(default=True, description="Whether the country is active")

    @validator("code")
    def uppercase_code(cls, v):
        return v.strip().upper() if v else v


class CountryCreate(CountryBase):
    """Schema for creating a new country."""


class CountryUpdate(BaseSchema):
    """Schema for updating an existing country."""

    code: Optional[str] = Field(None, min_length=2, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

    @validator("code")
    def uppercase_code(cls, v):
        return v.strip().upper() if v else v


class CountrySummary(UUIDSchema):
    """Lightweight country reference for lists and nesting."""

    code: str
    name: str
    is_active: bool


class CountryResponse(CountryBase, UUIDSchema, TimestampSchema):
    """Schema for country API responses."""

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    authorities_count: Optional[int] = Field(None, description="Number of authorities in this country")


# --------------------------------------------------------------------------- #
# Authority
# --------------------------------------------------------------------------- #
class AuthorityBase(BaseSchema):
    """Base authority schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Authority name")
    abbreviation: Optional[str] = Field(None, max_length=50, description="Authority abbreviation, e.g. 'FDA'")
    website: Optional[str] = Field(None, max_length=512, description="Authority website URL")
    description: Optional[str] = Field(None, description="Authority description")
    is_active: bool = Field(default=True, description="Whether the authority is active")


class AuthorityCreate(AuthorityBase):
    """Schema for creating a new authority."""

    country_id: UUID = Field(..., description="Parent country ID")


class AuthorityUpdate(BaseSchema):
    """Schema for updating an existing authority."""

    country_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    abbreviation: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AuthoritySummary(UUIDSchema):
    """Lightweight authority reference for lists and nesting."""

    country_id: UUID
    name: str
    abbreviation: Optional[str] = None
    is_active: bool


class AuthorityResponse(AuthorityBase, UUIDSchema, TimestampSchema):
    """Schema for authority API responses."""

    country_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    country: Optional[CountrySummary] = None
    regulations_count: Optional[int] = Field(None, description="Number of regulations under this authority")


# --------------------------------------------------------------------------- #
# Industry
# --------------------------------------------------------------------------- #
class IndustryBase(BaseSchema):
    """Base industry schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Industry name")
    code: str = Field(..., min_length=1, max_length=50, description="Industry code, e.g. 'PHARMA'")
    description: Optional[str] = Field(None, description="Industry description")
    is_active: bool = Field(default=True, description="Whether the industry is active")


class IndustryCreate(IndustryBase):
    """Schema for creating a new industry."""


class IndustryUpdate(BaseSchema):
    """Schema for updating an existing industry."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class IndustrySummary(UUIDSchema):
    """Lightweight industry reference for lists and nesting."""

    name: str
    code: str
    is_active: bool


class IndustryResponse(IndustryBase, UUIDSchema, TimestampSchema):
    """Schema for industry API responses."""

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    regulations_count: Optional[int] = Field(None, description="Number of regulations in this industry")


# --------------------------------------------------------------------------- #
# Regulation
# --------------------------------------------------------------------------- #
class RegulationBase(BaseSchema):
    """Base regulation schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Regulation name")
    code: str = Field(..., min_length=1, max_length=100, description="Regulation code")
    description: Optional[str] = Field(None, description="Regulation description")
    effective_date: Optional[date] = Field(None, description="Date the regulation takes effect")
    expiry_date: Optional[date] = Field(None, description="Date the regulation expires")
    version: Optional[str] = Field(None, max_length=50, description="Regulation version")
    status: RegulationStatusEnum = Field(
        default=RegulationStatusEnum.DRAFT, description="Regulation lifecycle status"
    )

    @validator("expiry_date")
    def expiry_after_effective(cls, v, values):
        effective = values.get("effective_date")
        if v and effective and v < effective:
            raise ValueError("expiry_date cannot be earlier than effective_date")
        return v


class RegulationCreate(RegulationBase):
    """Schema for creating a new regulation."""

    authority_id: UUID = Field(..., description="Issuing authority ID")
    industry_id: UUID = Field(..., description="Industry the regulation applies to")


class RegulationUpdate(BaseSchema):
    """Schema for updating an existing regulation."""

    authority_id: Optional[UUID] = None
    industry_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    version: Optional[str] = Field(None, max_length=50)
    status: Optional[RegulationStatusEnum] = None


class RegulationSummary(UUIDSchema):
    """Lightweight regulation reference for lists."""

    authority_id: UUID
    industry_id: UUID
    name: str
    code: str
    version: Optional[str] = None
    status: RegulationStatusEnum
    effective_date: Optional[date] = None


class RegulationResponse(RegulationBase, UUIDSchema, TimestampSchema):
    """Schema for regulation API responses."""

    authority_id: UUID
    industry_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    authority: Optional[AuthoritySummary] = None
    industry: Optional[IndustrySummary] = None
    submission_types_count: Optional[int] = Field(
        None, description="Number of submission types under this regulation"
    )


# --------------------------------------------------------------------------- #
# SubmissionType
# --------------------------------------------------------------------------- #
class SubmissionTypeBase(BaseSchema):
    """Base submission type schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Submission type name")
    code: str = Field(..., min_length=1, max_length=100, description="Submission type code")
    description: Optional[str] = Field(None, description="Submission type description")
    sequence_prefix: Optional[str] = Field(
        None, max_length=50, description="Prefix applied to generated sequence numbers"
    )
    allows_multiple_sequences: bool = Field(
        default=False, description="Whether multiple sequences are permitted for this type"
    )
    is_active: bool = Field(default=True, description="Whether the submission type is active")


class SubmissionTypeCreate(SubmissionTypeBase):
    """Schema for creating a new submission type."""

    regulation_id: UUID = Field(..., description="Parent regulation ID")


class SubmissionTypeUpdate(BaseSchema):
    """Schema for updating an existing submission type."""

    regulation_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    sequence_prefix: Optional[str] = Field(None, max_length=50)
    allows_multiple_sequences: Optional[bool] = None
    is_active: Optional[bool] = None


class SubmissionTypeSummary(UUIDSchema):
    """Lightweight submission type reference for lists and nesting."""

    regulation_id: UUID
    name: str
    code: str
    sequence_prefix: Optional[str] = None
    allows_multiple_sequences: bool
    is_active: bool


# --------------------------------------------------------------------------- #
# RiskClassification
# --------------------------------------------------------------------------- #
class RiskClassificationBase(BaseSchema):
    """Base risk classification schema with common fields."""

    code: str = Field(..., min_length=1, max_length=50, description="Risk classification code")
    name: str = Field(..., min_length=1, max_length=255, description="Risk classification name")
    description: Optional[str] = Field(None, description="Risk classification description")
    sort_order: int = Field(default=0, description="Ordering hint for display")


class RiskClassificationCreate(RiskClassificationBase):
    """Schema for creating a new risk classification."""


class RiskClassificationUpdate(BaseSchema):
    """Schema for updating an existing risk classification."""

    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sort_order: Optional[int] = None


class RiskClassificationSummary(UUIDSchema):
    """Lightweight risk classification reference for lists and nesting."""

    code: str
    name: str
    sort_order: int


class RiskClassificationResponse(RiskClassificationBase, UUIDSchema, TimestampSchema):
    """Schema for risk classification API responses."""

    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class SubmissionTypeResponse(SubmissionTypeBase, UUIDSchema, TimestampSchema):
    """Schema for submission type API responses."""

    regulation_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    regulation: Optional[RegulationSummary] = None
    risk_classifications: List[RiskClassificationSummary] = Field(
        default_factory=list, description="Risk classifications supported by this submission type"
    )


class SubmissionTypeRiskClassUpdate(BaseSchema):
    """Schema for replacing the full set of risk classifications on a submission type."""

    risk_classification_ids: List[UUID] = Field(
        ..., description="Complete set of risk classification IDs to assign"
    )


# --------------------------------------------------------------------------- #
# SubmissionProfile
# --------------------------------------------------------------------------- #
class SubmissionProfileBase(BaseSchema):
    """Base submission profile schema with common fields.

    Strategy configuration is referenced from the Configuration Registry via the
    four ``*_profile_id`` foreign keys rather than stored inline.
    """

    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    code: str = Field(..., min_length=1, max_length=100, description="Profile code")
    description: Optional[str] = Field(None, description="Profile description")

    # Configuration Registry references (ConfigurationProfile IDs).
    export_profile_id: Optional[UUID] = Field(
        None, description="Export ConfigurationProfile ID"
    )
    workflow_profile_id: Optional[UUID] = Field(
        None, description="Workflow ConfigurationProfile ID"
    )
    validation_profile_id: Optional[UUID] = Field(
        None, description="Validation ConfigurationProfile ID"
    )
    ai_pipeline_profile_id: Optional[UUID] = Field(
        None, description="AI pipeline ConfigurationProfile ID"
    )

    is_active: bool = Field(default=True, description="Whether the profile is active")


class SubmissionProfileCreate(SubmissionProfileBase):
    """Schema for creating a new submission profile."""

    submission_type_id: UUID = Field(..., description="Owning submission type ID")


class SubmissionProfileUpdate(BaseSchema):
    """Schema for updating an existing submission profile."""

    submission_type_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    export_profile_id: Optional[UUID] = None
    workflow_profile_id: Optional[UUID] = None
    validation_profile_id: Optional[UUID] = None
    ai_pipeline_profile_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class SubmissionProfileSummary(UUIDSchema):
    """Lightweight submission profile reference for lists."""

    submission_type_id: UUID
    name: str
    code: str
    is_active: bool


class SubmissionProfileResponse(SubmissionProfileBase, UUIDSchema, TimestampSchema):
    """Schema for submission profile API responses."""

    submission_type_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    # Resolved configuration profiles (nested, read-only).
    export_profile: Optional[ConfigurationProfileSummary] = None
    workflow_profile: Optional[ConfigurationProfileSummary] = None
    validation_profile: Optional[ConfigurationProfileSummary] = None
    ai_pipeline_profile: Optional[ConfigurationProfileSummary] = None


# --------------------------------------------------------------------------- #
# TemplateVersion
# --------------------------------------------------------------------------- #
class TemplateVersionBase(BaseSchema):
    """Base template version schema with common fields (versioned content only)."""

    version: str = Field(..., min_length=1, max_length=50, description="Template version label")
    effective_date: Optional[date] = Field(None, description="Date this version takes effect")
    expiry_date: Optional[date] = Field(None, description="Date this version expires")
    release_notes: Optional[str] = Field(None, description="Release notes for this version")
    status: TemplateStatusEnum = Field(
        default=TemplateStatusEnum.DRAFT, description="Template lifecycle status"
    )
    is_latest: bool = Field(
        default=False,
        description="Whether this is the latest version for its submission profile",
    )


class TemplateVersionCreate(TemplateVersionBase):
    """Schema for creating a new template version."""

    submission_profile_id: UUID = Field(..., description="Owning submission profile ID")


class TemplateVersionUpdate(BaseSchema):
    """Schema for updating an existing template version."""

    submission_profile_id: Optional[UUID] = None
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    release_notes: Optional[str] = None
    status: Optional[TemplateStatusEnum] = None
    is_latest: Optional[bool] = None


class TemplateVersionSummary(UUIDSchema):
    """Lightweight template version reference for lists."""

    submission_profile_id: UUID
    version: str
    status: TemplateStatusEnum
    is_latest: bool
    effective_date: Optional[date] = None


class TemplateVersionResponse(TemplateVersionBase, UUIDSchema, TimestampSchema):
    """Schema for template version API responses."""

    submission_profile_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    submission_profile: Optional[SubmissionProfileSummary] = None
    sections_count: Optional[int] = Field(
        None, description="Number of sections in this template version"
    )
    required_documents_count: Optional[int] = Field(
        None, description="Number of required documents in this template version"
    )
    validation_rules_count: Optional[int] = Field(
        None, description="Number of validation rules in this template version"
    )


# --------------------------------------------------------------------------- #
# TemplateSection
# --------------------------------------------------------------------------- #
class TemplateSectionBase(BaseSchema):
    """Base template section schema with common fields."""

    section_number: str = Field(..., min_length=1, max_length=50, description="Section number, e.g. '1.1'")
    title: str = Field(..., min_length=1, max_length=500, description="Section title")
    description: Optional[str] = Field(None, description="Section description")
    order: int = Field(default=0, description="Sort order among sibling sections")
    is_required: bool = Field(default=True, description="Whether the section is required")
    help_text: Optional[str] = Field(None, description="Guidance text for completing the section")


class TemplateSectionCreate(TemplateSectionBase):
    """Schema for creating a new template section."""

    template_version_id: UUID = Field(..., description="Owning template version ID")
    parent_id: Optional[UUID] = Field(None, description="Parent section ID (null for top-level)")


class TemplateSectionUpdate(BaseSchema):
    """Schema for updating an existing template section."""

    template_version_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    section_number: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    order: Optional[int] = None
    is_required: Optional[bool] = None
    help_text: Optional[str] = None


class TemplateSectionSummary(UUIDSchema):
    """Lightweight template section reference for lists."""

    template_version_id: UUID
    parent_id: Optional[UUID] = None
    section_number: str
    title: str
    order: int
    is_required: bool


class TemplateSectionResponse(TemplateSectionBase, UUIDSchema, TimestampSchema):
    """Schema for template section API responses."""

    template_version_id: UUID
    parent_id: Optional[UUID] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class TemplateSectionNode(TemplateSectionResponse):
    """Template section with its nested children, for hierarchical tree responses."""

    children: List["TemplateSectionNode"] = Field(default_factory=list)


TemplateSectionNode.model_rebuild()


# --------------------------------------------------------------------------- #
# RequiredDocument
# --------------------------------------------------------------------------- #
class RequiredDocumentBase(BaseSchema):
    """Base required document schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    required: bool = Field(default=True, description="Whether the document is mandatory")
    allowed_extensions: Optional[List[str]] = Field(
        None, description="Allowed file extensions, e.g. ['pdf', 'docx']"
    )
    accepted_mime_types: Optional[List[str]] = Field(
        None, description="Accepted MIME types, e.g. ['application/pdf']"
    )
    minimum_files: int = Field(default=0, ge=0, description="Minimum number of files")
    maximum_files: Optional[int] = Field(
        None, ge=1, description="Maximum number of files (null = unlimited)"
    )

    @validator("allowed_extensions")
    def normalize_extensions(cls, v):
        if v is None:
            return v
        # Normalize to lowercase without leading dots.
        return [ext.strip().lstrip(".").lower() for ext in v if ext and ext.strip()]

    @validator("maximum_files")
    def max_ge_min(cls, v, values):
        minimum = values.get("minimum_files")
        if v is not None and minimum is not None and v < minimum:
            raise ValueError("maximum_files cannot be less than minimum_files")
        return v


class RequiredDocumentCreate(RequiredDocumentBase):
    """Schema for creating a new required document."""

    template_version_id: UUID = Field(..., description="Owning template version ID")


class RequiredDocumentUpdate(BaseSchema):
    """Schema for updating an existing required document."""

    template_version_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    required: Optional[bool] = None
    allowed_extensions: Optional[List[str]] = None
    accepted_mime_types: Optional[List[str]] = None
    minimum_files: Optional[int] = Field(None, ge=0)
    maximum_files: Optional[int] = Field(None, ge=1)

    @validator("allowed_extensions")
    def normalize_extensions(cls, v):
        if v is None:
            return v
        return [ext.strip().lstrip(".").lower() for ext in v if ext and ext.strip()]


class RequiredDocumentSummary(UUIDSchema):
    """Lightweight required document reference for lists."""

    template_version_id: UUID
    name: str
    required: bool
    minimum_files: int
    maximum_files: Optional[int] = None


class RequiredDocumentResponse(RequiredDocumentBase, UUIDSchema, TimestampSchema):
    """Schema for required document API responses."""

    template_version_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# --------------------------------------------------------------------------- #
# ValidationRule
# --------------------------------------------------------------------------- #
class ValidationRuleBase(BaseSchema):
    """Base validation rule schema with common fields."""

    target_type: ValidationTargetTypeEnum = Field(..., description="What the rule targets")
    target_reference: Optional[str] = Field(
        None, max_length=255, description="Reference to the concrete target (e.g. section number)"
    )
    rule_type: str = Field(..., min_length=1, max_length=100, description="Rule type identifier")
    rule_expression: Optional[str] = Field(None, description="Expression/config interpreted by the engine")
    error_message: Optional[str] = Field(None, description="Message reported when the rule fails")
    severity: ValidationSeverityEnum = Field(
        default=ValidationSeverityEnum.ERROR, description="Severity of a violation"
    )
    is_active: bool = Field(default=True, description="Whether the rule is active")


class ValidationRuleCreate(ValidationRuleBase):
    """Schema for creating a new validation rule."""

    template_version_id: UUID = Field(..., description="Owning template version ID")


class ValidationRuleUpdate(BaseSchema):
    """Schema for updating an existing validation rule."""

    template_version_id: Optional[UUID] = None
    target_type: Optional[ValidationTargetTypeEnum] = None
    target_reference: Optional[str] = Field(None, max_length=255)
    rule_type: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_expression: Optional[str] = None
    error_message: Optional[str] = None
    severity: Optional[ValidationSeverityEnum] = None
    is_active: Optional[bool] = None


class ValidationRuleSummary(UUIDSchema):
    """Lightweight validation rule reference for lists."""

    template_version_id: UUID
    target_type: ValidationTargetTypeEnum
    target_reference: Optional[str] = None
    rule_type: str
    severity: ValidationSeverityEnum
    is_active: bool


class ValidationRuleResponse(ValidationRuleBase, UUIDSchema, TimestampSchema):
    """Schema for validation rule API responses."""

    template_version_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


# --------------------------------------------------------------------------- #
# SectionRule
# --------------------------------------------------------------------------- #
class SectionRuleBase(BaseSchema):
    """Base section rule schema with common fields."""

    rule_type: str = Field(..., min_length=1, max_length=100, description="Rule type identifier")
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence threshold (0.0–1.0) for the future matching engine"
    )


class SectionRuleCreate(SectionRuleBase):
    """Schema for creating a new section rule."""

    template_section_id: UUID = Field(..., description="Template section being linked")
    required_document_id: UUID = Field(..., description="Required document being linked")


class SectionRuleUpdate(BaseSchema):
    """Schema for updating an existing section rule."""

    template_section_id: Optional[UUID] = None
    required_document_id: Optional[UUID] = None
    rule_type: Optional[str] = Field(None, min_length=1, max_length=100)
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class SectionRuleSummary(UUIDSchema):
    """Lightweight section rule reference for lists."""

    template_section_id: UUID
    required_document_id: UUID
    rule_type: str
    confidence_threshold: Optional[float] = None


class SectionRuleResponse(SectionRuleBase, UUIDSchema, TimestampSchema):
    """Schema for section rule API responses."""

    template_section_id: UUID
    required_document_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
