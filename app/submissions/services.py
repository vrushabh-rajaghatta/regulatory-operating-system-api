"""
Atomic submission creation service.

Creating a submission resolves the full regulatory chain and then scaffolds every
dependent artifact — all inside a single database transaction:

    1. Find Country
    2. Find Authority
    3. Find Regulation
    4. Find Submission Type
    5. Find Risk Class
    6. Find latest active Template Version

    then automatically:
        - Create Submission
        - Create Dossier (sections, from the template version's sections)
        - Create Required Document placeholders
        - Create Validation Checklist

Nothing is committed until the very end. If any step fails the whole transaction
is rolled back, so a submission is never left half-built.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.auth.models import User
from app.submissions.models import Submission, SubmissionDocument, SubmissionValidationItem
from app.products.models import Product
from app.projects.models import Project
from app.dossier.models import DossierSection
from app.regulatory.models import (
    Country,
    Authority,
    Regulation,
    SubmissionType,
    SubmissionProfile,
    RiskClassification,
    TemplateVersion,
    TemplateSection,
    RequiredDocument,
    ValidationRule,
)
from app.regulatory.services import TemplateVersionService


SEQUENCE_NUMBER_WIDTH = 4


def _enum_value(value) -> str:
    """Coerce a SQLAlchemy Enum member (or plain string) to its string value."""
    return value.value if hasattr(value, "value") else str(value)


@dataclass
class GuidedSubmissionResult:
    """Everything created/resolved by an atomic submission creation."""

    submission: Submission
    country: Country
    authority: Authority
    regulation: Regulation
    submission_type: SubmissionType
    submission_profile: SubmissionProfile
    risk_classification: Optional[RiskClassification]
    template_version: TemplateVersion
    dossier_sections_count: int
    required_documents_count: int
    validation_items_count: int


class SubmissionCreationService:
    """Orchestrates atomic, transactional creation of a submission and its artifacts."""

    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------------- #
    # Public entry point
    # ----------------------------------------------------------------- #
    def create_guided(
        self,
        current_user: User,
        *,
        project_id: UUID,
        product_id: UUID,
        submission_profile_id: Optional[UUID] = None,
        submission_type_id: Optional[UUID] = None,
        risk_classification_id: Optional[UUID] = None,
        target_submission_date: Optional[date] = None,
    ) -> GuidedSubmissionResult:
        """
        Resolve the regulatory chain through the submission profile and create the
        submission + all dependent artifacts in a single transaction. Rolls back
        on any failure.

        Provide `submission_profile_id` (preferred) or, for backwards
        compatibility, `submission_type_id` (the submission type's active profile
        is resolved automatically). `risk_classification_id` is optional and, when
        given, is validated against the submission type.
        """
        try:
            # Access / ownership checks.
            project = self._resolve_project(project_id, current_user)
            self._resolve_product(product_id, project_id)

            # 1. Resolve the submission profile (explicit, or via submission type).
            submission_profile = self._resolve_submission_profile(
                submission_profile_id, submission_type_id
            )

            # Walk the chain upward from the profile's submission type.
            submission_type = self._resolve_submission_type(submission_profile.submission_type_id)
            regulation = self._resolve_regulation(submission_type)
            authority = self._resolve_authority(regulation)
            country = self._resolve_country(authority)

            # Risk class is optional; validate against the submission type if given.
            risk_classification = None
            if risk_classification_id is not None:
                risk_classification = self._resolve_risk_class(risk_classification_id)
                self._assert_risk_class_mapped(submission_type, risk_classification)

            # 2. Find the latest active template version for the profile.
            template_version = self._resolve_template_version_for_profile(submission_profile)

            # Create the submission row (flush, not commit, to get its id).
            submission = Submission(
                organization_id=project.organization_id,
                project_id=project_id,
                product_id=product_id,
                submission_profile_id=submission_profile.id,
                template_version_id=template_version.id,
                sequence_number=self._next_sequence_number(product_id),
                submission_type=submission_type.name,
                target_submission_date=target_submission_date,
            )
            self.db.add(submission)
            self.db.flush()

            # 3-6. Clone the template into submission artifacts (still in the transaction).
            dossier_sections_count = self._create_dossier_sections(submission, template_version)
            required_documents_count = self._create_required_document_placeholders(
                submission, template_version
            )
            validation_items_count = self._create_validation_checklist(submission, template_version)

            # Single commit — the whole thing is all-or-nothing.
            self.db.commit()
            self.db.refresh(submission)

            return GuidedSubmissionResult(
                submission=submission,
                country=country,
                authority=authority,
                regulation=regulation,
                submission_type=submission_type,
                submission_profile=submission_profile,
                risk_classification=risk_classification,
                template_version=template_version,
                dossier_sections_count=dossier_sections_count,
                required_documents_count=required_documents_count,
                validation_items_count=validation_items_count,
            )
        except HTTPException:
            # Validation/lookup failure — roll back anything already staged.
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Submission creation failed and was rolled back: {exc}",
            )

    # ----------------------------------------------------------------- #
    # Chain resolution (steps 1-6)
    # ----------------------------------------------------------------- #
    def _resolve_project(self, project_id: UUID, current_user: User) -> Project:
        query = self.db.query(Project).filter(Project.id == project_id)
        if not current_user.is_super_admin:
            query = query.filter(Project.organization_id == current_user.organization_id)
        project = query.first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    def _resolve_product(self, product_id: UUID, project_id: UUID) -> Product:
        product = self.db.query(Product).filter(
            and_(Product.id == product_id, Product.project_id == project_id)
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or does not belong to the specified project",
            )
        return product

    def _resolve_submission_type(self, submission_type_id: UUID) -> SubmissionType:
        submission_type = self.db.query(SubmissionType).filter(
            SubmissionType.id == submission_type_id
        ).first()
        if not submission_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission type not found")
        if not submission_type.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Submission type is not active")
        return submission_type

    def _resolve_regulation(self, submission_type: SubmissionType) -> Regulation:
        regulation = self.db.query(Regulation).filter(
            Regulation.id == submission_type.regulation_id
        ).first()
        if not regulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regulation not found for submission type",
            )
        return regulation

    def _resolve_authority(self, regulation: Regulation) -> Authority:
        authority = self.db.query(Authority).filter(Authority.id == regulation.authority_id).first()
        if not authority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Authority not found for regulation"
            )
        return authority

    def _resolve_country(self, authority: Authority) -> Country:
        country = self.db.query(Country).filter(Country.id == authority.country_id).first()
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Country not found for authority"
            )
        return country

    def _resolve_risk_class(self, risk_classification_id: UUID) -> RiskClassification:
        risk_classification = self.db.query(RiskClassification).filter(
            RiskClassification.id == risk_classification_id
        ).first()
        if not risk_classification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Risk classification not found"
            )
        return risk_classification

    def _assert_risk_class_mapped(
        self, submission_type: SubmissionType, risk_classification: RiskClassification
    ) -> None:
        if risk_classification not in submission_type.risk_classifications:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Risk classification is not associated with this submission type",
            )

    def _resolve_submission_profile(
        self,
        submission_profile_id: Optional[UUID],
        submission_type_id: Optional[UUID],
    ) -> SubmissionProfile:
        """
        Resolve the submission profile.

        Preferred: an explicit `submission_profile_id`. Backwards-compatible
        fallback: resolve the submission type's active profile (the earliest
        active one, deterministically) from `submission_type_id`.
        """
        if submission_profile_id is not None:
            profile = self.db.query(SubmissionProfile).filter(
                SubmissionProfile.id == submission_profile_id
            ).first()
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Submission profile not found"
                )
            if not profile.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Submission profile is not active"
                )
            if submission_type_id is not None and profile.submission_type_id != submission_type_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Submission profile does not belong to the specified submission type",
                )
            return profile

        if submission_type_id is not None:
            # Validate the submission type exists/active, then pick its active profile.
            self._resolve_submission_type(submission_type_id)
            profile = (
                self.db.query(SubmissionProfile)
                .filter(
                    SubmissionProfile.submission_type_id == submission_type_id,
                    SubmissionProfile.is_active.is_(True),
                )
                .order_by(SubmissionProfile.created_at.asc(), SubmissionProfile.name.asc())
                .first()
            )
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active submission profile is configured for this submission type",
                )
            return profile

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide submission_profile_id or submission_type_id",
        )

    def _resolve_template_version_for_profile(
        self, submission_profile: SubmissionProfile
    ) -> TemplateVersion:
        template_version = TemplateVersionService(self.db).resolve_latest_active(
            submission_profile.id
        )
        if not template_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"No active template version is configured for submission profile "
                    f"'{submission_profile.code}'"
                ),
            )
        return template_version

    # ----------------------------------------------------------------- #
    # Artifact scaffolding (no commits — caller owns the transaction)
    # ----------------------------------------------------------------- #
    def _next_sequence_number(self, product_id: UUID) -> str:
        existing = (
            self.db.query(Submission.sequence_number)
            .filter(Submission.product_id == product_id, Submission.sequence_number.isnot(None))
            .all()
        )
        max_seq = -1
        for (number,) in existing:
            try:
                max_seq = max(max_seq, int(number))
            except (TypeError, ValueError):
                continue
        return f"{max_seq + 1:0{SEQUENCE_NUMBER_WIDTH}d}"

    def _create_dossier_sections(
        self, submission: Submission, template_version: TemplateVersion
    ) -> int:
        """Materialize the template version's section hierarchy into dossier sections."""
        template_sections = (
            self.db.query(TemplateSection)
            .filter(TemplateSection.template_version_id == template_version.id)
            .order_by(TemplateSection.order, TemplateSection.section_number)
            .all()
        )
        if not template_sections:
            return 0

        # Phase 1: create a dossier section per template section, flush to assign ids.
        pairs = []
        for ts in template_sections:
            dossier_section = DossierSection(
                submission_id=submission.id,
                section_code=ts.section_number,
                section_title=ts.title,
                section_description=ts.description,
                is_required=ts.is_required,
                is_completed=False,
                completion_percentage=0,
                order_index=ts.order,
                template_source=f"TemplateVersion {template_version.version}",
            )
            self.db.add(dossier_section)
            pairs.append((ts, dossier_section))
        self.db.flush()

        # Phase 2: rewire parent links using the template->dossier id mapping.
        id_map = {ts.id: ds.id for ts, ds in pairs}
        for ts, dossier_section in pairs:
            if ts.parent_id is not None:
                dossier_section.parent_section_id = id_map.get(ts.parent_id)
        self.db.flush()
        return len(pairs)

    def _create_required_document_placeholders(
        self, submission: Submission, template_version: TemplateVersion
    ) -> int:
        """Create a placeholder slot per required document of the template version."""
        required_documents = (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.template_version_id == template_version.id)
            .order_by(RequiredDocument.name)
            .all()
        )
        for required_document in required_documents:
            self.db.add(
                SubmissionDocument(
                    submission_id=submission.id,
                    required_document_id=required_document.id,
                    document_name=required_document.name,
                    is_required=required_document.required,
                    status="pending",
                )
            )
        self.db.flush()
        return len(required_documents)

    def _create_validation_checklist(
        self, submission: Submission, template_version: TemplateVersion
    ) -> int:
        """Snapshot the template version's active validation rules into a checklist."""
        rules = (
            self.db.query(ValidationRule)
            .filter(
                ValidationRule.template_version_id == template_version.id,
                ValidationRule.is_active.is_(True),
            )
            .order_by(ValidationRule.target_type, ValidationRule.rule_type)
            .all()
        )
        for rule in rules:
            self.db.add(
                SubmissionValidationItem(
                    submission_id=submission.id,
                    validation_rule_id=rule.id,
                    target_type=_enum_value(rule.target_type),
                    target_reference=rule.target_reference,
                    rule_type=rule.rule_type,
                    error_message=rule.error_message,
                    severity=_enum_value(rule.severity),
                    status="pending",
                )
            )
        self.db.flush()
        return len(rules)
