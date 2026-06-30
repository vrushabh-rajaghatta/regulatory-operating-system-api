"""
Regulatory Engine CRUD services.

These services encapsulate the database logic for the regulatory master
entities so the router stays thin. They raise domain exceptions
(`NotFoundError`, `ConflictError`) that the router translates into HTTP
responses.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import nullslast
from sqlalchemy.orm import Session, joinedload, selectinload

from app.configuration.cache import configuration_cache
from app.regulatory.models import (
    Country, Authority, Industry, Regulation, SubmissionType, SubmissionProfile,
    RiskClassification, TemplateVersion, TemplateStatus, TemplateSection,
    RequiredDocument, ValidationRule, SectionRule,
)


class RegulatoryError(Exception):
    """Base class for regulatory service errors."""


class NotFoundError(RegulatoryError):
    """Raised when a requested entity does not exist."""


class ConflictError(RegulatoryError):
    """Raised when an operation violates a uniqueness/integrity constraint."""


# --------------------------------------------------------------------------- #
# Country
# --------------------------------------------------------------------------- #
class CountryService:
    """CRUD operations for Country master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, country_id: UUID) -> Country:
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise NotFoundError(f"Country not found: {country_id}")
        return country

    def get_by_code(self, code: str) -> Optional[Country]:
        return self.db.query(Country).filter(Country.code == code.upper()).first()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Country], int]:
        query = self.db.query(Country)
        if is_active is not None:
            query = query.filter(Country.is_active == is_active)
        if search:
            like = f"%{search}%"
            query = query.filter(Country.name.ilike(like) | Country.code.ilike(like))
        total = query.count()
        items = query.order_by(Country.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> Country:
        code = data.get("code")
        if code and self.get_by_code(code):
            raise ConflictError(f"Country with code '{code}' already exists")
        country = Country(**data, created_by=created_by, updated_by=created_by)
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country

    def update(self, country_id: UUID, data: dict, updated_by: Optional[str] = None) -> Country:
        country = self.get(country_id)
        new_code = data.get("code")
        if new_code and new_code != country.code:
            existing = self.get_by_code(new_code)
            if existing and existing.id != country.id:
                raise ConflictError(f"Country with code '{new_code}' already exists")
        for field, value in data.items():
            setattr(country, field, value)
        if updated_by is not None:
            country.updated_by = updated_by
        self.db.commit()
        self.db.refresh(country)
        return country

    def delete(self, country_id: UUID) -> None:
        country = self.get(country_id)
        self.db.delete(country)
        self.db.commit()


# --------------------------------------------------------------------------- #
# Authority
# --------------------------------------------------------------------------- #
class AuthorityService:
    """CRUD operations for Authority master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, authority_id: UUID, *, with_country: bool = False) -> Authority:
        query = self.db.query(Authority)
        if with_country:
            query = query.options(joinedload(Authority.country))
        authority = query.filter(Authority.id == authority_id).first()
        if not authority:
            raise NotFoundError(f"Authority not found: {authority_id}")
        return authority

    def _assert_country_exists(self, country_id: UUID) -> None:
        if not self.db.query(Country.id).filter(Country.id == country_id).first():
            raise NotFoundError(f"Country not found: {country_id}")

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        country_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Authority], int]:
        query = self.db.query(Authority).options(joinedload(Authority.country))
        if country_id:
            query = query.filter(Authority.country_id == country_id)
        if is_active is not None:
            query = query.filter(Authority.is_active == is_active)
        if search:
            like = f"%{search}%"
            query = query.filter(
                Authority.name.ilike(like) | Authority.abbreviation.ilike(like)
            )
        total = query.count()
        items = query.order_by(Authority.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> Authority:
        self._assert_country_exists(data["country_id"])
        authority = Authority(**data, created_by=created_by, updated_by=created_by)
        self.db.add(authority)
        self.db.commit()
        self.db.refresh(authority)
        return authority

    def update(self, authority_id: UUID, data: dict, updated_by: Optional[str] = None) -> Authority:
        authority = self.get(authority_id)
        if data.get("country_id"):
            self._assert_country_exists(data["country_id"])
        for field, value in data.items():
            setattr(authority, field, value)
        if updated_by is not None:
            authority.updated_by = updated_by
        self.db.commit()
        self.db.refresh(authority)
        return authority

    def delete(self, authority_id: UUID) -> None:
        authority = self.get(authority_id)
        self.db.delete(authority)
        self.db.commit()


# --------------------------------------------------------------------------- #
# Industry
# --------------------------------------------------------------------------- #
class IndustryService:
    """CRUD operations for Industry master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, industry_id: UUID) -> Industry:
        industry = self.db.query(Industry).filter(Industry.id == industry_id).first()
        if not industry:
            raise NotFoundError(f"Industry not found: {industry_id}")
        return industry

    def get_by_code(self, code: str) -> Optional[Industry]:
        return self.db.query(Industry).filter(Industry.code == code).first()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Industry], int]:
        query = self.db.query(Industry)
        if is_active is not None:
            query = query.filter(Industry.is_active == is_active)
        if search:
            like = f"%{search}%"
            query = query.filter(Industry.name.ilike(like) | Industry.code.ilike(like))
        total = query.count()
        items = query.order_by(Industry.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> Industry:
        code = data.get("code")
        if code and self.get_by_code(code):
            raise ConflictError(f"Industry with code '{code}' already exists")
        industry = Industry(**data, created_by=created_by, updated_by=created_by)
        self.db.add(industry)
        self.db.commit()
        self.db.refresh(industry)
        return industry

    def update(self, industry_id: UUID, data: dict, updated_by: Optional[str] = None) -> Industry:
        industry = self.get(industry_id)
        new_code = data.get("code")
        if new_code and new_code != industry.code:
            existing = self.get_by_code(new_code)
            if existing and existing.id != industry.id:
                raise ConflictError(f"Industry with code '{new_code}' already exists")
        for field, value in data.items():
            setattr(industry, field, value)
        if updated_by is not None:
            industry.updated_by = updated_by
        self.db.commit()
        self.db.refresh(industry)
        return industry

    def delete(self, industry_id: UUID) -> None:
        industry = self.get(industry_id)
        self.db.delete(industry)
        self.db.commit()


# --------------------------------------------------------------------------- #
# Regulation
# --------------------------------------------------------------------------- #
class RegulationService:
    """CRUD operations for Regulation master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, regulation_id: UUID, *, with_relations: bool = False) -> Regulation:
        query = self.db.query(Regulation)
        if with_relations:
            query = query.options(
                joinedload(Regulation.authority),
                joinedload(Regulation.industry),
            )
        regulation = query.filter(Regulation.id == regulation_id).first()
        if not regulation:
            raise NotFoundError(f"Regulation not found: {regulation_id}")
        return regulation

    def _assert_authority_exists(self, authority_id: UUID) -> None:
        if not self.db.query(Authority.id).filter(Authority.id == authority_id).first():
            raise NotFoundError(f"Authority not found: {authority_id}")

    def _assert_industry_exists(self, industry_id: UUID) -> None:
        if not self.db.query(Industry.id).filter(Industry.id == industry_id).first():
            raise NotFoundError(f"Industry not found: {industry_id}")

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        authority_id: Optional[UUID] = None,
        industry_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Regulation], int]:
        query = self.db.query(Regulation).options(
            joinedload(Regulation.authority),
            joinedload(Regulation.industry),
        )
        if authority_id:
            query = query.filter(Regulation.authority_id == authority_id)
        if industry_id:
            query = query.filter(Regulation.industry_id == industry_id)
        if status:
            query = query.filter(Regulation.status == status)
        if search:
            like = f"%{search}%"
            query = query.filter(Regulation.name.ilike(like) | Regulation.code.ilike(like))
        total = query.count()
        items = query.order_by(Regulation.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> Regulation:
        self._assert_authority_exists(data["authority_id"])
        self._assert_industry_exists(data["industry_id"])
        regulation = Regulation(**data, created_by=created_by, updated_by=created_by)
        self.db.add(regulation)
        self.db.commit()
        self.db.refresh(regulation)
        return regulation

    def update(self, regulation_id: UUID, data: dict, updated_by: Optional[str] = None) -> Regulation:
        regulation = self.get(regulation_id)
        if data.get("authority_id"):
            self._assert_authority_exists(data["authority_id"])
        if data.get("industry_id"):
            self._assert_industry_exists(data["industry_id"])
        for field, value in data.items():
            setattr(regulation, field, value)
        if updated_by is not None:
            regulation.updated_by = updated_by
        self.db.commit()
        self.db.refresh(regulation)
        return regulation

    def delete(self, regulation_id: UUID) -> None:
        regulation = self.get(regulation_id)
        self.db.delete(regulation)
        self.db.commit()


# --------------------------------------------------------------------------- #
# SubmissionType
# --------------------------------------------------------------------------- #
class SubmissionTypeService:
    """CRUD operations for SubmissionType master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, submission_type_id: UUID, *, with_regulation: bool = False) -> SubmissionType:
        query = self.db.query(SubmissionType).options(
            selectinload(SubmissionType.risk_classifications)
        )
        if with_regulation:
            query = query.options(joinedload(SubmissionType.regulation))
        submission_type = query.filter(SubmissionType.id == submission_type_id).first()
        if not submission_type:
            raise NotFoundError(f"Submission type not found: {submission_type_id}")
        return submission_type

    def _assert_regulation_exists(self, regulation_id: UUID) -> None:
        if not self.db.query(Regulation.id).filter(Regulation.id == regulation_id).first():
            raise NotFoundError(f"Regulation not found: {regulation_id}")

    def _code_in_use(self, regulation_id: UUID, code: str, exclude_id: Optional[UUID] = None) -> bool:
        query = self.db.query(SubmissionType.id).filter(
            SubmissionType.regulation_id == regulation_id,
            SubmissionType.code == code,
        )
        if exclude_id is not None:
            query = query.filter(SubmissionType.id != exclude_id)
        return query.first() is not None

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        regulation_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[SubmissionType], int]:
        query = self.db.query(SubmissionType).options(joinedload(SubmissionType.regulation))
        if regulation_id:
            query = query.filter(SubmissionType.regulation_id == regulation_id)
        if is_active is not None:
            query = query.filter(SubmissionType.is_active == is_active)
        if search:
            like = f"%{search}%"
            query = query.filter(
                SubmissionType.name.ilike(like) | SubmissionType.code.ilike(like)
            )
        total = query.count()
        items = query.order_by(SubmissionType.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> SubmissionType:
        self._assert_regulation_exists(data["regulation_id"])
        if self._code_in_use(data["regulation_id"], data["code"]):
            raise ConflictError(
                f"Submission type with code '{data['code']}' already exists for this regulation"
            )
        submission_type = SubmissionType(**data, created_by=created_by, updated_by=created_by)
        self.db.add(submission_type)
        self.db.commit()
        self.db.refresh(submission_type)
        return submission_type

    def update(self, submission_type_id: UUID, data: dict, updated_by: Optional[str] = None) -> SubmissionType:
        submission_type = self.get(submission_type_id)
        if data.get("regulation_id"):
            self._assert_regulation_exists(data["regulation_id"])
        target_regulation = data.get("regulation_id", submission_type.regulation_id)
        target_code = data.get("code", submission_type.code)
        if self._code_in_use(target_regulation, target_code, exclude_id=submission_type.id):
            raise ConflictError(
                f"Submission type with code '{target_code}' already exists for this regulation"
            )
        for field, value in data.items():
            setattr(submission_type, field, value)
        if updated_by is not None:
            submission_type.updated_by = updated_by
        self.db.commit()
        self.db.refresh(submission_type)
        return submission_type

    def delete(self, submission_type_id: UUID) -> None:
        submission_type = self.get(submission_type_id)
        self.db.delete(submission_type)
        self.db.commit()

    # --- risk classification mapping ------------------------------------- #
    def _get_risk_class(self, risk_classification_id: UUID) -> RiskClassification:
        risk_class = (
            self.db.query(RiskClassification)
            .filter(RiskClassification.id == risk_classification_id)
            .first()
        )
        if not risk_class:
            raise NotFoundError(f"Risk classification not found: {risk_classification_id}")
        return risk_class

    def set_risk_classifications(
        self, submission_type_id: UUID, risk_classification_ids: List[UUID]
    ) -> SubmissionType:
        """Replace the full set of risk classifications for a submission type."""
        submission_type = self.get(submission_type_id)
        unique_ids = list(dict.fromkeys(risk_classification_ids))  # preserve order, drop dups
        risk_classes = []
        for risk_id in unique_ids:
            risk_classes.append(self._get_risk_class(risk_id))
        submission_type.risk_classifications = risk_classes
        self.db.commit()
        self.db.refresh(submission_type)
        return submission_type

    def add_risk_classification(
        self, submission_type_id: UUID, risk_classification_id: UUID
    ) -> SubmissionType:
        """Attach a single risk classification (idempotent)."""
        submission_type = self.get(submission_type_id)
        risk_class = self._get_risk_class(risk_classification_id)
        if risk_class not in submission_type.risk_classifications:
            submission_type.risk_classifications.append(risk_class)
            self.db.commit()
            self.db.refresh(submission_type)
        return submission_type

    def remove_risk_classification(
        self, submission_type_id: UUID, risk_classification_id: UUID
    ) -> SubmissionType:
        """Detach a single risk classification (idempotent)."""
        submission_type = self.get(submission_type_id)
        risk_class = self._get_risk_class(risk_classification_id)
        if risk_class in submission_type.risk_classifications:
            submission_type.risk_classifications.remove(risk_class)
            self.db.commit()
            self.db.refresh(submission_type)
        return submission_type


# --------------------------------------------------------------------------- #
# RiskClassification
# --------------------------------------------------------------------------- #
class RiskClassificationService:
    """CRUD operations for RiskClassification master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, risk_classification_id: UUID) -> RiskClassification:
        risk_class = (
            self.db.query(RiskClassification)
            .filter(RiskClassification.id == risk_classification_id)
            .first()
        )
        if not risk_class:
            raise NotFoundError(f"Risk classification not found: {risk_classification_id}")
        return risk_class

    def get_by_code(self, code: str) -> Optional[RiskClassification]:
        return self.db.query(RiskClassification).filter(RiskClassification.code == code).first()

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[RiskClassification], int]:
        query = self.db.query(RiskClassification)
        if search:
            like = f"%{search}%"
            query = query.filter(
                RiskClassification.name.ilike(like) | RiskClassification.code.ilike(like)
            )
        total = query.count()
        items = (
            query.order_by(RiskClassification.sort_order, RiskClassification.name)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> RiskClassification:
        code = data.get("code")
        if code and self.get_by_code(code):
            raise ConflictError(f"Risk classification with code '{code}' already exists")
        risk_class = RiskClassification(**data, created_by=created_by, updated_by=created_by)
        self.db.add(risk_class)
        self.db.commit()
        self.db.refresh(risk_class)
        return risk_class

    def update(self, risk_classification_id: UUID, data: dict, updated_by: Optional[str] = None) -> RiskClassification:
        risk_class = self.get(risk_classification_id)
        new_code = data.get("code")
        if new_code and new_code != risk_class.code:
            existing = self.get_by_code(new_code)
            if existing and existing.id != risk_class.id:
                raise ConflictError(f"Risk classification with code '{new_code}' already exists")
        for field, value in data.items():
            setattr(risk_class, field, value)
        if updated_by is not None:
            risk_class.updated_by = updated_by
        self.db.commit()
        self.db.refresh(risk_class)
        return risk_class

    def delete(self, risk_classification_id: UUID) -> None:
        risk_class = self.get(risk_classification_id)
        self.db.delete(risk_class)
        self.db.commit()


# --------------------------------------------------------------------------- #
# TemplateVersion
# --------------------------------------------------------------------------- #
class TemplateVersionService:
    """
    CRUD operations for TemplateVersion.

    Owns the `is_latest` invariant: at most one template version is flagged
    latest per submission profile scope.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, template_version_id: UUID, *, with_relations: bool = False) -> TemplateVersion:
        query = self.db.query(TemplateVersion)
        if with_relations:
            query = query.options(joinedload(TemplateVersion.submission_profile))
        template_version = query.filter(TemplateVersion.id == template_version_id).first()
        if not template_version:
            raise NotFoundError(f"Template version not found: {template_version_id}")
        return template_version

    def _assert_submission_profile_exists(self, submission_profile_id: UUID) -> None:
        if not self.db.query(SubmissionProfile.id).filter(
            SubmissionProfile.id == submission_profile_id
        ).first():
            raise NotFoundError(f"Submission profile not found: {submission_profile_id}")

    def _version_in_use(
        self,
        submission_profile_id: UUID,
        version: str,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(TemplateVersion.id).filter(
            TemplateVersion.submission_profile_id == submission_profile_id,
            TemplateVersion.version == version,
        )
        if exclude_id is not None:
            query = query.filter(TemplateVersion.id != exclude_id)
        return query.first() is not None

    def _unset_latest(
        self,
        submission_profile_id: UUID,
        exclude_id: Optional[UUID] = None,
    ) -> None:
        """Clear is_latest for all siblings in the same profile scope."""
        query = self.db.query(TemplateVersion).filter(
            TemplateVersion.submission_profile_id == submission_profile_id,
            TemplateVersion.is_latest.is_(True),
        )
        if exclude_id is not None:
            query = query.filter(TemplateVersion.id != exclude_id)
        for sibling in query.all():
            sibling.is_latest = False

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        submission_profile_id: Optional[UUID] = None,
        status: Optional[str] = None,
        is_latest: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[TemplateVersion], int]:
        query = self.db.query(TemplateVersion).options(
            joinedload(TemplateVersion.submission_profile)
        )
        if submission_profile_id:
            query = query.filter(TemplateVersion.submission_profile_id == submission_profile_id)
        if status:
            query = query.filter(TemplateVersion.status == status)
        if is_latest is not None:
            query = query.filter(TemplateVersion.is_latest.is_(is_latest))
        if search:
            like = f"%{search}%"
            query = query.filter(
                TemplateVersion.version.ilike(like) | TemplateVersion.release_notes.ilike(like)
            )
        total = query.count()
        items = (
            query.order_by(TemplateVersion.version.desc()).offset(offset).limit(limit).all()
        )
        return items, total

    def get_latest(self, submission_profile_id: UUID) -> Optional[TemplateVersion]:
        """Resolve the latest (is_latest-flagged) template version for a profile."""
        return (
            self.db.query(TemplateVersion)
            .filter(
                TemplateVersion.submission_profile_id == submission_profile_id,
                TemplateVersion.is_latest.is_(True),
            )
            .first()
        )

    def resolve_latest_active(self, submission_profile_id: UUID) -> Optional[TemplateVersion]:
        """
        Resolve the latest *active* template version for a submission profile.

        Considers only ACTIVE versions and prefers the one flagged ``is_latest``;
        otherwise falls back to the most recent by effective date, then version.
        """
        return (
            self.db.query(TemplateVersion)
            .filter(
                TemplateVersion.submission_profile_id == submission_profile_id,
                TemplateVersion.status == TemplateStatus.ACTIVE,
            )
            .order_by(
                TemplateVersion.is_latest.desc(),
                nullslast(TemplateVersion.effective_date.desc()),
                TemplateVersion.version.desc(),
            )
            .first()
        )

    def resolve_latest_active_for_submission_type(
        self, submission_type_id: UUID
    ) -> Optional[TemplateVersion]:
        """
        Resolve the latest active template version across all profiles of a
        submission type. Bridges callers that work at the submission-type level
        (e.g. guided submission creation) to the profile-based hierarchy.
        """
        return (
            self.db.query(TemplateVersion)
            .join(SubmissionProfile, TemplateVersion.submission_profile_id == SubmissionProfile.id)
            .filter(
                SubmissionProfile.submission_type_id == submission_type_id,
                TemplateVersion.status == TemplateStatus.ACTIVE,
            )
            .order_by(
                TemplateVersion.is_latest.desc(),
                nullslast(TemplateVersion.effective_date.desc()),
                TemplateVersion.version.desc(),
                TemplateVersion.created_at.desc(),
            )
            .first()
        )

    def create(self, data: dict, created_by: Optional[str] = None) -> TemplateVersion:
        self._assert_submission_profile_exists(data["submission_profile_id"])
        if self._version_in_use(data["submission_profile_id"], data["version"]):
            raise ConflictError(
                f"Template version '{data['version']}' already exists for this submission profile"
            )
        template_version = TemplateVersion(**data, created_by=created_by, updated_by=created_by)
        if template_version.is_latest:
            self._unset_latest(template_version.submission_profile_id)
        self.db.add(template_version)
        self.db.commit()
        self.db.refresh(template_version)
        configuration_cache.clear()  # template version changed — drop cache
        return template_version

    def update(self, template_version_id: UUID, data: dict, updated_by: Optional[str] = None) -> TemplateVersion:
        template_version = self.get(template_version_id)
        if data.get("submission_profile_id"):
            self._assert_submission_profile_exists(data["submission_profile_id"])

        target_profile = data.get("submission_profile_id", template_version.submission_profile_id)
        target_version = data.get("version", template_version.version)
        if self._version_in_use(target_profile, target_version, exclude_id=template_version.id):
            raise ConflictError(
                f"Template version '{target_version}' already exists for this submission profile"
            )

        for field, value in data.items():
            setattr(template_version, field, value)
        if updated_by is not None:
            template_version.updated_by = updated_by

        # Maintain the single-latest invariant within the (possibly new) profile scope.
        if template_version.is_latest:
            self._unset_latest(
                template_version.submission_profile_id,
                exclude_id=template_version.id,
            )

        self.db.commit()
        self.db.refresh(template_version)
        configuration_cache.clear()  # template version changed — drop cache
        return template_version

    def set_latest(self, template_version_id: UUID) -> TemplateVersion:
        """Mark a template version as the latest for its profile scope."""
        template_version = self.get(template_version_id)
        self._unset_latest(
            template_version.submission_profile_id,
            exclude_id=template_version.id,
        )
        template_version.is_latest = True
        self.db.commit()
        self.db.refresh(template_version)
        configuration_cache.clear()  # template version changed — drop cache
        return template_version

    def delete(self, template_version_id: UUID) -> None:
        template_version = self.get(template_version_id)
        self.db.delete(template_version)
        self.db.commit()
        configuration_cache.clear()  # template version removed — drop cache


# --------------------------------------------------------------------------- #
# TemplateSection
# --------------------------------------------------------------------------- #
class TemplateSectionService:
    """
    CRUD operations for TemplateSection, including hierarchical (parent_id) and
    tree-shaped reads.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, section_id: UUID) -> TemplateSection:
        section = self.db.query(TemplateSection).filter(TemplateSection.id == section_id).first()
        if not section:
            raise NotFoundError(f"Template section not found: {section_id}")
        return section

    def _assert_template_version_exists(self, template_version_id: UUID) -> None:
        if not self.db.query(TemplateVersion.id).filter(
            TemplateVersion.id == template_version_id
        ).first():
            raise NotFoundError(f"Template version not found: {template_version_id}")

    def _resolve_parent(self, parent_id: UUID, template_version_id: UUID) -> TemplateSection:
        """Validate that a parent exists and lives in the same template version."""
        parent = self.db.query(TemplateSection).filter(TemplateSection.id == parent_id).first()
        if not parent:
            raise NotFoundError(f"Parent template section not found: {parent_id}")
        if parent.template_version_id != template_version_id:
            raise ConflictError("Parent section must belong to the same template version")
        return parent

    def _is_descendant(self, candidate_parent_id: UUID, section_id: UUID) -> bool:
        """True if candidate_parent_id is the section itself or one of its descendants."""
        current_id = candidate_parent_id
        # Walk up from the candidate parent; if we reach section_id, it's a cycle.
        while current_id is not None:
            if current_id == section_id:
                return True
            row = (
                self.db.query(TemplateSection.parent_id)
                .filter(TemplateSection.id == current_id)
                .first()
            )
            current_id = row[0] if row else None
        return False

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        template_version_id: Optional[UUID] = None,
        parent_id: Optional[UUID] = None,
        top_level_only: bool = False,
        search: Optional[str] = None,
    ) -> tuple[List[TemplateSection], int]:
        query = self.db.query(TemplateSection)
        if template_version_id:
            query = query.filter(TemplateSection.template_version_id == template_version_id)
        if top_level_only:
            query = query.filter(TemplateSection.parent_id.is_(None))
        elif parent_id is not None:
            query = query.filter(TemplateSection.parent_id == parent_id)
        if search:
            like = f"%{search}%"
            query = query.filter(
                TemplateSection.title.ilike(like) | TemplateSection.section_number.ilike(like)
            )
        total = query.count()
        items = (
            query.order_by(TemplateSection.order, TemplateSection.section_number)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def get_tree(self, template_version_id: UUID) -> List[dict]:
        """Return the section hierarchy for a template version as nested dicts."""
        self._assert_template_version_exists(template_version_id)
        sections = (
            self.db.query(TemplateSection)
            .filter(TemplateSection.template_version_id == template_version_id)
            .order_by(TemplateSection.order, TemplateSection.section_number)
            .all()
        )

        nodes: dict = {}
        roots: List[dict] = []
        for section in sections:
            nodes[section.id] = {
                "id": section.id,
                "template_version_id": section.template_version_id,
                "parent_id": section.parent_id,
                "section_number": section.section_number,
                "title": section.title,
                "description": section.description,
                "order": section.order,
                "is_required": section.is_required,
                "help_text": section.help_text,
                "created_at": section.created_at,
                "updated_at": section.updated_at,
                "created_by": section.created_by,
                "updated_by": section.updated_by,
                "children": [],
            }

        for section in sections:
            node = nodes[section.id]
            if section.parent_id and section.parent_id in nodes:
                nodes[section.parent_id]["children"].append(node)
            else:
                roots.append(node)
        return roots

    def create(self, data: dict, created_by: Optional[str] = None) -> TemplateSection:
        self._assert_template_version_exists(data["template_version_id"])
        if data.get("parent_id"):
            self._resolve_parent(data["parent_id"], data["template_version_id"])
        section = TemplateSection(**data, created_by=created_by, updated_by=created_by)
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        return section

    def update(self, section_id: UUID, data: dict, updated_by: Optional[str] = None) -> TemplateSection:
        section = self.get(section_id)
        target_version = data.get("template_version_id", section.template_version_id)
        if data.get("template_version_id"):
            self._assert_template_version_exists(data["template_version_id"])

        if "parent_id" in data and data["parent_id"] is not None:
            new_parent_id = data["parent_id"]
            if new_parent_id == section.id:
                raise ConflictError("A section cannot be its own parent")
            if self._is_descendant(new_parent_id, section.id):
                raise ConflictError("Cannot move a section under one of its own descendants")
            self._resolve_parent(new_parent_id, target_version)

        for field, value in data.items():
            setattr(section, field, value)
        if updated_by is not None:
            section.updated_by = updated_by
        self.db.commit()
        self.db.refresh(section)
        return section

    def delete(self, section_id: UUID) -> None:
        """Delete a section; child sections are removed via cascade."""
        section = self.get(section_id)
        self.db.delete(section)
        self.db.commit()


# --------------------------------------------------------------------------- #
# RequiredDocument
# --------------------------------------------------------------------------- #
class RequiredDocumentService:
    """CRUD operations for RequiredDocument master data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, required_document_id: UUID) -> RequiredDocument:
        document = (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.id == required_document_id)
            .first()
        )
        if not document:
            raise NotFoundError(f"Required document not found: {required_document_id}")
        return document

    def _assert_template_version_exists(self, template_version_id: UUID) -> None:
        if not self.db.query(TemplateVersion.id).filter(
            TemplateVersion.id == template_version_id
        ).first():
            raise NotFoundError(f"Template version not found: {template_version_id}")

    def _name_in_use(
        self, template_version_id: UUID, name: str, exclude_id: Optional[UUID] = None
    ) -> bool:
        query = self.db.query(RequiredDocument.id).filter(
            RequiredDocument.template_version_id == template_version_id,
            RequiredDocument.name == name,
        )
        if exclude_id is not None:
            query = query.filter(RequiredDocument.id != exclude_id)
        return query.first() is not None

    def list_for_template_version(self, template_version_id: UUID) -> List[RequiredDocument]:
        """Return all required documents for a template version (unpaginated)."""
        return (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.template_version_id == template_version_id)
            .order_by(RequiredDocument.name)
            .all()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        template_version_id: Optional[UUID] = None,
        required: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[RequiredDocument], int]:
        query = self.db.query(RequiredDocument)
        if template_version_id:
            query = query.filter(RequiredDocument.template_version_id == template_version_id)
        if required is not None:
            query = query.filter(RequiredDocument.required.is_(required))
        if search:
            like = f"%{search}%"
            query = query.filter(RequiredDocument.name.ilike(like))
        total = query.count()
        items = query.order_by(RequiredDocument.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> RequiredDocument:
        self._assert_template_version_exists(data["template_version_id"])
        if self._name_in_use(data["template_version_id"], data["name"]):
            raise ConflictError(
                f"Required document '{data['name']}' already exists for this template version"
            )
        document = RequiredDocument(**data, created_by=created_by, updated_by=created_by)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update(self, required_document_id: UUID, data: dict, updated_by: Optional[str] = None) -> RequiredDocument:
        document = self.get(required_document_id)
        if data.get("template_version_id"):
            self._assert_template_version_exists(data["template_version_id"])
        target_version = data.get("template_version_id", document.template_version_id)
        target_name = data.get("name", document.name)
        if self._name_in_use(target_version, target_name, exclude_id=document.id):
            raise ConflictError(
                f"Required document '{target_name}' already exists for this template version"
            )
        for field, value in data.items():
            setattr(document, field, value)
        if updated_by is not None:
            document.updated_by = updated_by
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, required_document_id: UUID) -> None:
        document = self.get(required_document_id)
        self.db.delete(document)
        self.db.commit()


# --------------------------------------------------------------------------- #
# ValidationRule
# --------------------------------------------------------------------------- #
class ValidationRuleService:
    """
    CRUD operations for ValidationRule.

    Data-model only: rules are stored and managed here, but no rule is
    evaluated/executed by this service.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, rule_id: UUID) -> ValidationRule:
        rule = self.db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
        if not rule:
            raise NotFoundError(f"Validation rule not found: {rule_id}")
        return rule

    def _assert_template_version_exists(self, template_version_id: UUID) -> None:
        if not self.db.query(TemplateVersion.id).filter(
            TemplateVersion.id == template_version_id
        ).first():
            raise NotFoundError(f"Template version not found: {template_version_id}")

    def list_for_template_version(self, template_version_id: UUID) -> List[ValidationRule]:
        """Return all validation rules for a template version (unpaginated)."""
        return (
            self.db.query(ValidationRule)
            .filter(ValidationRule.template_version_id == template_version_id)
            .order_by(ValidationRule.target_type, ValidationRule.rule_type)
            .all()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        template_version_id: Optional[UUID] = None,
        target_type: Optional[str] = None,
        rule_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ValidationRule], int]:
        query = self.db.query(ValidationRule)
        if template_version_id:
            query = query.filter(ValidationRule.template_version_id == template_version_id)
        if target_type:
            query = query.filter(ValidationRule.target_type == target_type)
        if rule_type:
            query = query.filter(ValidationRule.rule_type == rule_type)
        if severity:
            query = query.filter(ValidationRule.severity == severity)
        if is_active is not None:
            query = query.filter(ValidationRule.is_active.is_(is_active))
        if search:
            like = f"%{search}%"
            query = query.filter(
                ValidationRule.rule_type.ilike(like)
                | ValidationRule.target_reference.ilike(like)
                | ValidationRule.error_message.ilike(like)
            )
        total = query.count()
        items = (
            query.order_by(ValidationRule.target_type, ValidationRule.rule_type)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> ValidationRule:
        self._assert_template_version_exists(data["template_version_id"])
        rule = ValidationRule(**data, created_by=created_by, updated_by=created_by)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update(self, rule_id: UUID, data: dict, updated_by: Optional[str] = None) -> ValidationRule:
        rule = self.get(rule_id)
        if data.get("template_version_id"):
            self._assert_template_version_exists(data["template_version_id"])
        for field, value in data.items():
            setattr(rule, field, value)
        if updated_by is not None:
            rule.updated_by = updated_by
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, rule_id: UUID) -> None:
        rule = self.get(rule_id)
        self.db.delete(rule)
        self.db.commit()


# --------------------------------------------------------------------------- #
# SectionRule
# --------------------------------------------------------------------------- #
class SectionRuleService:
    """
    CRUD operations for SectionRule (template section <-> required document links).

    Data-model only: links are stored and managed here, with no AI/matching
    logic applied to ``rule_type`` or ``confidence_threshold``.
    """

    def __init__(self, db: Session):
        self.db = db

    def get(self, section_rule_id: UUID) -> SectionRule:
        rule = self.db.query(SectionRule).filter(SectionRule.id == section_rule_id).first()
        if not rule:
            raise NotFoundError(f"Section rule not found: {section_rule_id}")
        return rule

    def _get_section(self, template_section_id: UUID) -> TemplateSection:
        section = (
            self.db.query(TemplateSection)
            .filter(TemplateSection.id == template_section_id)
            .first()
        )
        if not section:
            raise NotFoundError(f"Template section not found: {template_section_id}")
        return section

    def _get_document(self, required_document_id: UUID) -> RequiredDocument:
        document = (
            self.db.query(RequiredDocument)
            .filter(RequiredDocument.id == required_document_id)
            .first()
        )
        if not document:
            raise NotFoundError(f"Required document not found: {required_document_id}")
        return document

    def _assert_same_template_version(
        self, template_section_id: UUID, required_document_id: UUID
    ) -> None:
        """A section may only be linked to a document from the same template version."""
        section = self._get_section(template_section_id)
        document = self._get_document(required_document_id)
        if section.template_version_id != document.template_version_id:
            raise ConflictError(
                "Template section and required document must belong to the same template version"
            )

    def _link_in_use(
        self,
        template_section_id: UUID,
        required_document_id: UUID,
        rule_type: str,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(SectionRule.id).filter(
            SectionRule.template_section_id == template_section_id,
            SectionRule.required_document_id == required_document_id,
            SectionRule.rule_type == rule_type,
        )
        if exclude_id is not None:
            query = query.filter(SectionRule.id != exclude_id)
        return query.first() is not None

    def list_for_section(self, template_section_id: UUID) -> List[SectionRule]:
        """Return all rules (document links) for a template section (unpaginated)."""
        return (
            self.db.query(SectionRule)
            .filter(SectionRule.template_section_id == template_section_id)
            .order_by(SectionRule.rule_type)
            .all()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        template_section_id: Optional[UUID] = None,
        required_document_id: Optional[UUID] = None,
        rule_type: Optional[str] = None,
    ) -> tuple[List[SectionRule], int]:
        query = self.db.query(SectionRule)
        if template_section_id:
            query = query.filter(SectionRule.template_section_id == template_section_id)
        if required_document_id:
            query = query.filter(SectionRule.required_document_id == required_document_id)
        if rule_type:
            query = query.filter(SectionRule.rule_type == rule_type)
        total = query.count()
        items = query.order_by(SectionRule.rule_type).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> SectionRule:
        self._assert_same_template_version(
            data["template_section_id"], data["required_document_id"]
        )
        if self._link_in_use(
            data["template_section_id"], data["required_document_id"], data["rule_type"]
        ):
            raise ConflictError(
                "A section rule with this rule type already links these section and document"
            )
        rule = SectionRule(**data, created_by=created_by, updated_by=created_by)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update(self, section_rule_id: UUID, data: dict, updated_by: Optional[str] = None) -> SectionRule:
        rule = self.get(section_rule_id)
        target_section = data.get("template_section_id", rule.template_section_id)
        target_document = data.get("required_document_id", rule.required_document_id)
        target_rule_type = data.get("rule_type", rule.rule_type)

        if "template_section_id" in data or "required_document_id" in data:
            self._assert_same_template_version(target_section, target_document)
        if self._link_in_use(target_section, target_document, target_rule_type, exclude_id=rule.id):
            raise ConflictError(
                "A section rule with this rule type already links these section and document"
            )

        for field, value in data.items():
            setattr(rule, field, value)
        if updated_by is not None:
            rule.updated_by = updated_by
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, section_rule_id: UUID) -> None:
        rule = self.get(section_rule_id)
        self.db.delete(rule)
        self.db.commit()


# --------------------------------------------------------------------------- #
# SubmissionProfile
# --------------------------------------------------------------------------- #
class SubmissionProfileService:
    """CRUD operations for SubmissionProfile (configuration per submission type)."""

    # Submission profile fields that reference a ConfigurationProfile.
    _CONFIG_FK_FIELDS = (
        "export_profile_id",
        "workflow_profile_id",
        "validation_profile_id",
        "ai_pipeline_profile_id",
    )

    def __init__(self, db: Session):
        self.db = db

    def get(self, profile_id: UUID, *, with_submission_type: bool = False) -> SubmissionProfile:
        query = self.db.query(SubmissionProfile).options(
            joinedload(SubmissionProfile.export_profile),
            joinedload(SubmissionProfile.workflow_profile),
            joinedload(SubmissionProfile.validation_profile),
            joinedload(SubmissionProfile.ai_pipeline_profile),
        )
        if with_submission_type:
            query = query.options(joinedload(SubmissionProfile.submission_type))
        profile = query.filter(SubmissionProfile.id == profile_id).first()
        if not profile:
            raise NotFoundError(f"Submission profile not found: {profile_id}")
        return profile

    def _assert_submission_type_exists(self, submission_type_id: UUID) -> None:
        if not self.db.query(SubmissionType.id).filter(
            SubmissionType.id == submission_type_id
        ).first():
            raise NotFoundError(f"Submission type not found: {submission_type_id}")

    def _assert_config_profiles_exist(self, data: dict) -> None:
        """Validate that any provided ConfigurationProfile FK references exist."""
        from app.configuration.models import ConfigurationProfile

        for field in self._CONFIG_FK_FIELDS:
            profile_id = data.get(field)
            if profile_id is None:
                continue
            if not self.db.query(ConfigurationProfile.id).filter(
                ConfigurationProfile.id == profile_id
            ).first():
                raise NotFoundError(f"Configuration profile not found: {profile_id}")

    def _code_in_use(
        self, submission_type_id: UUID, code: str, exclude_id: Optional[UUID] = None
    ) -> bool:
        query = self.db.query(SubmissionProfile.id).filter(
            SubmissionProfile.submission_type_id == submission_type_id,
            SubmissionProfile.code == code,
        )
        if exclude_id is not None:
            query = query.filter(SubmissionProfile.id != exclude_id)
        return query.first() is not None

    def list_for_submission_type(self, submission_type_id: UUID) -> List[SubmissionProfile]:
        """Return all profiles for a submission type (unpaginated)."""
        return (
            self.db.query(SubmissionProfile)
            .filter(SubmissionProfile.submission_type_id == submission_type_id)
            .order_by(SubmissionProfile.name)
            .all()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        submission_type_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[SubmissionProfile], int]:
        query = self.db.query(SubmissionProfile)
        if submission_type_id:
            query = query.filter(SubmissionProfile.submission_type_id == submission_type_id)
        if is_active is not None:
            query = query.filter(SubmissionProfile.is_active.is_(is_active))
        if search:
            like = f"%{search}%"
            query = query.filter(
                SubmissionProfile.name.ilike(like) | SubmissionProfile.code.ilike(like)
            )
        total = query.count()
        items = query.order_by(SubmissionProfile.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> SubmissionProfile:
        self._assert_submission_type_exists(data["submission_type_id"])
        self._assert_config_profiles_exist(data)
        if self._code_in_use(data["submission_type_id"], data["code"]):
            raise ConflictError(
                f"Submission profile with code '{data['code']}' already exists for this submission type"
            )
        profile = SubmissionProfile(**data, created_by=created_by, updated_by=created_by)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        configuration_cache.clear()  # submission profile wiring changed — drop cache
        return profile

    def update(self, profile_id: UUID, data: dict, updated_by: Optional[str] = None) -> SubmissionProfile:
        profile = self.get(profile_id)
        if data.get("submission_type_id"):
            self._assert_submission_type_exists(data["submission_type_id"])
        self._assert_config_profiles_exist(data)
        target_type = data.get("submission_type_id", profile.submission_type_id)
        target_code = data.get("code", profile.code)
        if self._code_in_use(target_type, target_code, exclude_id=profile.id):
            raise ConflictError(
                f"Submission profile with code '{target_code}' already exists for this submission type"
            )
        for field, value in data.items():
            setattr(profile, field, value)
        if updated_by is not None:
            profile.updated_by = updated_by
        self.db.commit()
        self.db.refresh(profile)
        configuration_cache.clear()  # submission profile wiring changed — drop cache
        return profile

    def delete(self, profile_id: UUID) -> None:
        profile = self.get(profile_id)
        self.db.delete(profile)
        self.db.commit()
        configuration_cache.clear()  # submission profile removed — drop cache
