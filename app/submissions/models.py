"""
Submission models for managing regulatory submissions.
"""

from sqlalchemy import Column, String, Text, Boolean, Enum, ForeignKey, Date, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.models import BaseModel, AuditMixin


class SubmissionStatus(str, enum.Enum):
    """Submission status enumeration."""
    DRAFT = "draft"
    AI_PROCESSING = "ai_processing"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


class Submission(BaseModel, AuditMixin):
    """
    Regulatory submission model.
    
    Represents a regulatory submission for a specific product,
    tracking the submission lifecycle and approval process.
    """
    
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("product_id", "sequence_number", name="uq_submissions_product_id_sequence_number"),
    )
    
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    # Links to the governing regulatory chain. Nullable so existing submissions and
    # the legacy submission_type-string flow are unaffected.
    submission_profile_id = Column(
        UUID(as_uuid=True), ForeignKey("submission_profiles.id"), nullable=True, index=True
    )
    template_version_id = Column(
        UUID(as_uuid=True), ForeignKey("template_versions.id"), nullable=True, index=True
    )
    # Zero-padded sequential number scoped to the parent product (e.g. "0000", "0001").
    # Unique per product; the same value can repeat across different products.
    sequence_number = Column(String(32), nullable=False, index=True)
    submission_type = Column(String(255), nullable=True)  # e.g., "Medical Device License", "Amendment"
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False, index=True)
    # Reference/tracking number assigned by the regulatory authority (jurisdiction-agnostic).
    authority_reference = Column(String(255), nullable=True, index=True)
    target_submission_date = Column(Date, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(255), nullable=True)
    
    # Relationships
    organization = relationship("app.auth.models.Organization")
    project = relationship("app.projects.models.Project", back_populates="submissions")
    product = relationship("app.products.models.Product", back_populates="submissions")
    submission_profile = relationship("app.regulatory.models.SubmissionProfile")
    template_version = relationship("app.regulatory.models.TemplateVersion")
    dossier_sections = relationship("app.dossier.models.DossierSection", back_populates="submission", cascade="all, delete-orphan")
    missing_content_alerts = relationship("app.validation.models.MissingContent", back_populates="submission", cascade="all, delete-orphan")
    consistency_checks = relationship("app.validation.models.ConsistencyCheck", back_populates="submission", cascade="all, delete-orphan")
    documents = relationship("SubmissionDocument", back_populates="submission", cascade="all, delete-orphan")
    validation_items = relationship("SubmissionValidationItem", back_populates="submission", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, sequence_number='{self.sequence_number}', status='{self.status}')>"


class SubmissionDocument(BaseModel, AuditMixin):
    """
    A per-submission placeholder/slot for a required document.

    Created automatically from a template version's ``RequiredDocument`` set when
    a submission is created. Holds a snapshot of the requirement (name / required
    flag) so the slot stays meaningful even if the template later changes, plus a
    fulfilment ``status``.
    """

    __tablename__ = "submission_documents"

    submission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Source requirement; SET NULL on delete so the placeholder survives template edits.
    required_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("required_documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    document_name = Column(String(255), nullable=False)  # snapshot of the requirement name
    is_required = Column(Boolean, default=True, nullable=False)  # snapshot of required flag
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending / provided

    # Relationships
    submission = relationship("Submission", back_populates="documents")
    required_document = relationship("app.regulatory.models.RequiredDocument")

    def __repr__(self) -> str:
        return (
            f"<SubmissionDocument(id={self.id}, submission={self.submission_id}, "
            f"name='{self.document_name}', status='{self.status}')>"
        )


class SubmissionValidationItem(BaseModel, AuditMixin):
    """
    A per-submission validation checklist item.

    Created automatically from the governing template version's
    ``ValidationRule`` set when a submission is created. Snapshots the rule
    (target, type, message, severity) so the checklist stays meaningful even if
    the template later changes, plus a fulfilment ``status``.
    """

    __tablename__ = "submission_validation_items"

    submission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Source rule; SET NULL on delete so the checklist item survives template edits.
    validation_rule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("validation_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    target_type = Column(String(50), nullable=False)  # snapshot (Document/Section/Submission)
    target_reference = Column(String(255), nullable=True)  # snapshot
    rule_type = Column(String(100), nullable=False)  # snapshot
    error_message = Column(Text, nullable=True)  # snapshot
    severity = Column(String(50), nullable=False)  # snapshot (Error/Warning/Info)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending / passed / failed

    # Relationships
    submission = relationship("Submission", back_populates="validation_items")
    validation_rule = relationship("app.regulatory.models.ValidationRule")

    def __repr__(self) -> str:
        return (
            f"<SubmissionValidationItem(id={self.id}, submission={self.submission_id}, "
            f"rule_type='{self.rule_type}', status='{self.status}')>"
        )