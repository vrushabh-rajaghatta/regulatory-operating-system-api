"""
Regulatory Engine API router.

Exposes full CRUD for the regulatory master entities:
    /countries, /authorities, /industries, /regulations

These are global reference entities, so endpoints are not organization-scoped;
they are protected by the platform-wide authentication dependency applied in
`app.main`. Audit fields (`created_by` / `updated_by`) are stamped from the
authenticated user.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.core.database import get_db
from app.core.schemas import PaginationParams, PaginatedResponse, MessageResponse
from app.regulatory.services import (
    CountryService,
    AuthorityService,
    IndustryService,
    RegulationService,
    SubmissionTypeService,
    RiskClassificationService,
    TemplateVersionService,
    TemplateSectionService,
    RequiredDocumentService,
    ValidationRuleService,
    SectionRuleService,
    SubmissionProfileService,
    NotFoundError,
    ConflictError,
)
from app.regulatory.schemas import (
    CountryCreate,
    CountryUpdate,
    CountryResponse,
    CountrySummary,
    AuthorityCreate,
    AuthorityUpdate,
    AuthorityResponse,
    AuthoritySummary,
    IndustryCreate,
    IndustryUpdate,
    IndustryResponse,
    IndustrySummary,
    RegulationCreate,
    RegulationUpdate,
    RegulationResponse,
    RegulationSummary,
    SubmissionTypeCreate,
    SubmissionTypeUpdate,
    SubmissionTypeResponse,
    SubmissionTypeSummary,
    SubmissionTypeRiskClassUpdate,
    RiskClassificationCreate,
    RiskClassificationUpdate,
    RiskClassificationResponse,
    RiskClassificationSummary,
    TemplateVersionCreate,
    TemplateVersionUpdate,
    TemplateVersionResponse,
    TemplateVersionSummary,
    TemplateSectionCreate,
    TemplateSectionUpdate,
    TemplateSectionResponse,
    TemplateSectionSummary,
    TemplateSectionNode,
    RequiredDocumentCreate,
    RequiredDocumentUpdate,
    RequiredDocumentResponse,
    RequiredDocumentSummary,
    ValidationRuleCreate,
    ValidationRuleUpdate,
    ValidationRuleResponse,
    ValidationRuleSummary,
    SectionRuleCreate,
    SectionRuleUpdate,
    SectionRuleResponse,
    SectionRuleSummary,
    SubmissionProfileCreate,
    SubmissionProfileUpdate,
    SubmissionProfileResponse,
    SubmissionProfileSummary,
)

router = APIRouter()


def _actor(current_user: User) -> str:
    """Identify the acting user for audit fields."""
    return current_user.username


def _handle(error: Exception):
    """Translate a regulatory service error into an HTTPException."""
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    raise error


# --------------------------------------------------------------------------- #
# Countries
# --------------------------------------------------------------------------- #
@router.post("/countries", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
async def create_country(
    payload: CountryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new country."""
    try:
        return CountryService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/countries", response_model=PaginatedResponse)
async def list_countries(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List countries with optional filtering and pagination."""
    items, total = CountryService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        is_active=is_active,
        search=search,
    )
    summaries = [CountrySummary.model_validate(c) for c in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/countries/{country_id}", response_model=CountryResponse)
async def get_country(
    country_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single country by ID."""
    try:
        country = CountryService(db).get(country_id)
    except NotFoundError as exc:
        _handle(exc)
    country.authorities_count = len(country.authorities)
    return country


@router.put("/countries/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: UUID,
    payload: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing country."""
    try:
        return CountryService(db).update(
            country_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/countries/{country_id}", response_model=MessageResponse)
async def delete_country(
    country_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a country (and its authorities/regulations via cascade)."""
    try:
        CountryService(db).delete(country_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Country deleted successfully")


# --------------------------------------------------------------------------- #
# Authorities
# --------------------------------------------------------------------------- #
@router.post("/authorities", response_model=AuthorityResponse, status_code=status.HTTP_201_CREATED)
async def create_authority(
    payload: AuthorityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new authority."""
    try:
        return AuthorityService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/authorities", response_model=PaginatedResponse)
async def list_authorities(
    pagination: PaginationParams = Depends(),
    country_id: Optional[UUID] = Query(None, description="Filter by country"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or abbreviation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List authorities with optional filtering and pagination."""
    items, total = AuthorityService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        country_id=country_id,
        is_active=is_active,
        search=search,
    )
    summaries = [AuthoritySummary.model_validate(a) for a in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/authorities/{authority_id}", response_model=AuthorityResponse)
async def get_authority(
    authority_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single authority by ID."""
    try:
        authority = AuthorityService(db).get(authority_id, with_country=True)
    except NotFoundError as exc:
        _handle(exc)
    authority.regulations_count = len(authority.regulations)
    return authority


@router.put("/authorities/{authority_id}", response_model=AuthorityResponse)
async def update_authority(
    authority_id: UUID,
    payload: AuthorityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing authority."""
    try:
        return AuthorityService(db).update(
            authority_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/authorities/{authority_id}", response_model=MessageResponse)
async def delete_authority(
    authority_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an authority (and its regulations via cascade)."""
    try:
        AuthorityService(db).delete(authority_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Authority deleted successfully")


# --------------------------------------------------------------------------- #
# Industries
# --------------------------------------------------------------------------- #
@router.post("/industries", response_model=IndustryResponse, status_code=status.HTTP_201_CREATED)
async def create_industry(
    payload: IndustryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new industry."""
    try:
        return IndustryService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/industries", response_model=PaginatedResponse)
async def list_industries(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List industries with optional filtering and pagination."""
    items, total = IndustryService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        is_active=is_active,
        search=search,
    )
    summaries = [IndustrySummary.model_validate(i) for i in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/industries/{industry_id}", response_model=IndustryResponse)
async def get_industry(
    industry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single industry by ID."""
    try:
        industry = IndustryService(db).get(industry_id)
    except NotFoundError as exc:
        _handle(exc)
    industry.regulations_count = len(industry.regulations)
    return industry


@router.put("/industries/{industry_id}", response_model=IndustryResponse)
async def update_industry(
    industry_id: UUID,
    payload: IndustryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing industry."""
    try:
        return IndustryService(db).update(
            industry_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/industries/{industry_id}", response_model=MessageResponse)
async def delete_industry(
    industry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an industry (and its regulations via cascade)."""
    try:
        IndustryService(db).delete(industry_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Industry deleted successfully")


# --------------------------------------------------------------------------- #
# Regulations
# --------------------------------------------------------------------------- #
@router.post("/regulations", response_model=RegulationResponse, status_code=status.HTTP_201_CREATED)
async def create_regulation(
    payload: RegulationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new regulation."""
    try:
        return RegulationService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/regulations", response_model=PaginatedResponse)
async def list_regulations(
    pagination: PaginationParams = Depends(),
    authority_id: Optional[UUID] = Query(None, description="Filter by authority"),
    industry_id: Optional[UUID] = Query(None, description="Filter by industry"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List regulations with optional filtering and pagination."""
    items, total = RegulationService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        authority_id=authority_id,
        industry_id=industry_id,
        status=status_filter,
        search=search,
    )
    summaries = [RegulationSummary.model_validate(r) for r in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/regulations/{regulation_id}", response_model=RegulationResponse)
async def get_regulation(
    regulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single regulation by ID."""
    try:
        regulation = RegulationService(db).get(regulation_id, with_relations=True)
    except NotFoundError as exc:
        _handle(exc)
    regulation.submission_types_count = len(regulation.submission_types)
    return regulation


@router.put("/regulations/{regulation_id}", response_model=RegulationResponse)
async def update_regulation(
    regulation_id: UUID,
    payload: RegulationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing regulation."""
    try:
        return RegulationService(db).update(
            regulation_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/regulations/{regulation_id}", response_model=MessageResponse)
async def delete_regulation(
    regulation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a regulation."""
    try:
        RegulationService(db).delete(regulation_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Regulation deleted successfully")


# --------------------------------------------------------------------------- #
# Submission Types
# --------------------------------------------------------------------------- #
@router.post("/submission-types", response_model=SubmissionTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_submission_type(
    payload: SubmissionTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new submission type."""
    try:
        return SubmissionTypeService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/submission-types", response_model=PaginatedResponse)
async def list_submission_types(
    pagination: PaginationParams = Depends(),
    regulation_id: Optional[UUID] = Query(None, description="Filter by regulation"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List submission types with optional filtering and pagination."""
    items, total = SubmissionTypeService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        regulation_id=regulation_id,
        is_active=is_active,
        search=search,
    )
    summaries = [SubmissionTypeSummary.model_validate(st) for st in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/submission-types/{submission_type_id}", response_model=SubmissionTypeResponse)
async def get_submission_type(
    submission_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single submission type by ID."""
    try:
        return SubmissionTypeService(db).get(submission_type_id, with_regulation=True)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/submission-types/{submission_type_id}", response_model=SubmissionTypeResponse)
async def update_submission_type(
    submission_type_id: UUID,
    payload: SubmissionTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing submission type."""
    try:
        return SubmissionTypeService(db).update(
            submission_type_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/submission-types/{submission_type_id}", response_model=MessageResponse)
async def delete_submission_type(
    submission_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a submission type."""
    try:
        SubmissionTypeService(db).delete(submission_type_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Submission type deleted successfully")


# --- submission type <-> risk classification mapping ----------------------- #
@router.get(
    "/submission-types/{submission_type_id}/risk-classifications",
    response_model=list[RiskClassificationSummary],
)
async def list_submission_type_risk_classifications(
    submission_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the risk classifications a submission type supports."""
    try:
        submission_type = SubmissionTypeService(db).get(submission_type_id)
    except NotFoundError as exc:
        _handle(exc)
    return [
        RiskClassificationSummary.model_validate(rc)
        for rc in submission_type.risk_classifications
    ]


@router.put(
    "/submission-types/{submission_type_id}/risk-classifications",
    response_model=SubmissionTypeResponse,
)
async def set_submission_type_risk_classifications(
    submission_type_id: UUID,
    payload: SubmissionTypeRiskClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Replace the full set of risk classifications for a submission type."""
    try:
        return SubmissionTypeService(db).set_risk_classifications(
            submission_type_id, payload.risk_classification_ids
        )
    except NotFoundError as exc:
        _handle(exc)


@router.post(
    "/submission-types/{submission_type_id}/risk-classifications/{risk_classification_id}",
    response_model=SubmissionTypeResponse,
)
async def add_submission_type_risk_classification(
    submission_type_id: UUID,
    risk_classification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach a single risk classification to a submission type."""
    try:
        return SubmissionTypeService(db).add_risk_classification(
            submission_type_id, risk_classification_id
        )
    except NotFoundError as exc:
        _handle(exc)


@router.delete(
    "/submission-types/{submission_type_id}/risk-classifications/{risk_classification_id}",
    response_model=SubmissionTypeResponse,
)
async def remove_submission_type_risk_classification(
    submission_type_id: UUID,
    risk_classification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detach a single risk classification from a submission type."""
    try:
        return SubmissionTypeService(db).remove_risk_classification(
            submission_type_id, risk_classification_id
        )
    except NotFoundError as exc:
        _handle(exc)


# --------------------------------------------------------------------------- #
# Risk Classifications
# --------------------------------------------------------------------------- #
@router.post("/risk-classifications", response_model=RiskClassificationResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_classification(
    payload: RiskClassificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new risk classification."""
    try:
        return RiskClassificationService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/risk-classifications", response_model=PaginatedResponse)
async def list_risk_classifications(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List risk classifications with optional filtering and pagination."""
    items, total = RiskClassificationService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        search=search,
    )
    summaries = [RiskClassificationSummary.model_validate(rc) for rc in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/risk-classifications/{risk_classification_id}", response_model=RiskClassificationResponse)
async def get_risk_classification(
    risk_classification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single risk classification by ID."""
    try:
        return RiskClassificationService(db).get(risk_classification_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/risk-classifications/{risk_classification_id}", response_model=RiskClassificationResponse)
async def update_risk_classification(
    risk_classification_id: UUID,
    payload: RiskClassificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing risk classification."""
    try:
        return RiskClassificationService(db).update(
            risk_classification_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/risk-classifications/{risk_classification_id}", response_model=MessageResponse)
async def delete_risk_classification(
    risk_classification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a risk classification (also removes its submission-type mappings)."""
    try:
        RiskClassificationService(db).delete(risk_classification_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Risk classification deleted successfully")


# --------------------------------------------------------------------------- #
# Template Versions
# --------------------------------------------------------------------------- #
@router.post("/template-versions", response_model=TemplateVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_template_version(
    payload: TemplateVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new template version for a submission type / risk classification."""
    try:
        return TemplateVersionService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/template-versions", response_model=PaginatedResponse)
async def list_template_versions(
    pagination: PaginationParams = Depends(),
    submission_profile_id: Optional[UUID] = Query(None, description="Filter by submission profile"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    is_latest: Optional[bool] = Query(None, description="Filter by latest flag"),
    search: Optional[str] = Query(None, description="Search by version or release notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List template versions with optional filtering and pagination."""
    items, total = TemplateVersionService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        submission_profile_id=submission_profile_id,
        status=status_filter,
        is_latest=is_latest,
        search=search,
    )
    summaries = [TemplateVersionSummary.model_validate(tv) for tv in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/template-versions/latest", response_model=TemplateVersionResponse)
async def get_latest_template_version(
    submission_profile_id: Optional[UUID] = Query(None, description="Submission profile ID"),
    submission_type_id: Optional[UUID] = Query(
        None, description="Submission type ID (resolves the latest active across its profiles)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Resolve the latest active template version.

    Provide `submission_profile_id` (preferred) or `submission_type_id` (resolves
    across all of the submission type's profiles).
    """
    service = TemplateVersionService(db)
    if submission_profile_id:
        template_version = service.resolve_latest_active(submission_profile_id)
        scope = "submission profile"
    elif submission_type_id:
        template_version = service.resolve_latest_active_for_submission_type(submission_type_id)
        scope = "submission type"
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide submission_profile_id or submission_type_id",
        )
    if not template_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active template version for this {scope}",
        )
    return template_version


@router.get("/template-versions/{template_version_id}", response_model=TemplateVersionResponse)
async def get_template_version(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single template version by ID."""
    try:
        template_version = TemplateVersionService(db).get(template_version_id, with_relations=True)
    except NotFoundError as exc:
        _handle(exc)
    template_version.sections_count = len(template_version.sections)
    template_version.required_documents_count = len(template_version.required_documents)
    template_version.validation_rules_count = len(template_version.validation_rules)
    return template_version


@router.put("/template-versions/{template_version_id}", response_model=TemplateVersionResponse)
async def update_template_version(
    template_version_id: UUID,
    payload: TemplateVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing template version."""
    try:
        return TemplateVersionService(db).update(
            template_version_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.post("/template-versions/{template_version_id}/set-latest", response_model=TemplateVersionResponse)
async def set_latest_template_version(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a template version as the latest for its submission type / risk class scope."""
    try:
        return TemplateVersionService(db).set_latest(template_version_id)
    except NotFoundError as exc:
        _handle(exc)


@router.delete("/template-versions/{template_version_id}", response_model=MessageResponse)
async def delete_template_version(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a template version."""
    try:
        TemplateVersionService(db).delete(template_version_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Template version deleted successfully")


# --- template version sections (scoped reads) ------------------------------ #
@router.get(
    "/template-versions/{template_version_id}/sections",
    response_model=list[TemplateSectionSummary],
)
async def list_template_version_sections(
    template_version_id: UUID,
    top_level_only: bool = Query(False, description="Return only top-level sections"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the (flat) sections of a template version."""
    try:
        TemplateVersionService(db).get(template_version_id)
    except NotFoundError as exc:
        _handle(exc)
    items, _ = TemplateSectionService(db).list(
        template_version_id=template_version_id,
        top_level_only=top_level_only,
        limit=10_000,
    )
    return [TemplateSectionSummary.model_validate(s) for s in items]


@router.get(
    "/template-versions/{template_version_id}/section-tree",
    response_model=list[TemplateSectionNode],
)
async def get_template_version_section_tree(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the hierarchical section tree for a template version."""
    try:
        return TemplateSectionService(db).get_tree(template_version_id)
    except NotFoundError as exc:
        _handle(exc)


# --------------------------------------------------------------------------- #
# Template Sections
# --------------------------------------------------------------------------- #
@router.post("/template-sections", response_model=TemplateSectionResponse, status_code=status.HTTP_201_CREATED)
async def create_template_section(
    payload: TemplateSectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new template section (optionally nested under a parent)."""
    try:
        return TemplateSectionService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/template-sections", response_model=PaginatedResponse)
async def list_template_sections(
    pagination: PaginationParams = Depends(),
    template_version_id: Optional[UUID] = Query(None, description="Filter by template version"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent section"),
    search: Optional[str] = Query(None, description="Search by title or section number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List template sections with optional filtering and pagination."""
    items, total = TemplateSectionService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        template_version_id=template_version_id,
        parent_id=parent_id,
        search=search,
    )
    summaries = [TemplateSectionSummary.model_validate(s) for s in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/template-sections/{section_id}", response_model=TemplateSectionResponse)
async def get_template_section(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single template section by ID."""
    try:
        return TemplateSectionService(db).get(section_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/template-sections/{section_id}", response_model=TemplateSectionResponse)
async def update_template_section(
    section_id: UUID,
    payload: TemplateSectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing template section."""
    try:
        return TemplateSectionService(db).update(
            section_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/template-sections/{section_id}", response_model=MessageResponse)
async def delete_template_section(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a template section (child sections are removed via cascade)."""
    try:
        TemplateSectionService(db).delete(section_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Template section deleted successfully")


# --- template version required documents (scoped read) --------------------- #
@router.get(
    "/template-versions/{template_version_id}/required-documents",
    response_model=list[RequiredDocumentSummary],
)
async def list_template_version_required_documents(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the required documents defined for a template version."""
    try:
        TemplateVersionService(db).get(template_version_id)
    except NotFoundError as exc:
        _handle(exc)
    documents = RequiredDocumentService(db).list_for_template_version(template_version_id)
    return [RequiredDocumentSummary.model_validate(d) for d in documents]


# --------------------------------------------------------------------------- #
# Required Documents
# --------------------------------------------------------------------------- #
@router.post("/required-documents", response_model=RequiredDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_required_document(
    payload: RequiredDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new required document for a template version."""
    try:
        return RequiredDocumentService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/required-documents", response_model=PaginatedResponse)
async def list_required_documents(
    pagination: PaginationParams = Depends(),
    template_version_id: Optional[UUID] = Query(None, description="Filter by template version"),
    required: Optional[bool] = Query(None, description="Filter by required flag"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List required documents with optional filtering and pagination."""
    items, total = RequiredDocumentService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        template_version_id=template_version_id,
        required=required,
        search=search,
    )
    summaries = [RequiredDocumentSummary.model_validate(d) for d in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/required-documents/{required_document_id}", response_model=RequiredDocumentResponse)
async def get_required_document(
    required_document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single required document by ID."""
    try:
        return RequiredDocumentService(db).get(required_document_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/required-documents/{required_document_id}", response_model=RequiredDocumentResponse)
async def update_required_document(
    required_document_id: UUID,
    payload: RequiredDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing required document."""
    try:
        return RequiredDocumentService(db).update(
            required_document_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/required-documents/{required_document_id}", response_model=MessageResponse)
async def delete_required_document(
    required_document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a required document."""
    try:
        RequiredDocumentService(db).delete(required_document_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Required document deleted successfully")


# --- template version validation rules (scoped read) ----------------------- #
@router.get(
    "/template-versions/{template_version_id}/validation-rules",
    response_model=list[ValidationRuleSummary],
)
async def list_template_version_validation_rules(
    template_version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the validation rules defined for a template version."""
    try:
        TemplateVersionService(db).get(template_version_id)
    except NotFoundError as exc:
        _handle(exc)
    rules = ValidationRuleService(db).list_for_template_version(template_version_id)
    return [ValidationRuleSummary.model_validate(r) for r in rules]


# --------------------------------------------------------------------------- #
# Validation Rules
# --------------------------------------------------------------------------- #
@router.post("/validation-rules", response_model=ValidationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_validation_rule(
    payload: ValidationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new validation rule for a template version."""
    try:
        return ValidationRuleService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/validation-rules", response_model=PaginatedResponse)
async def list_validation_rules(
    pagination: PaginationParams = Depends(),
    template_version_id: Optional[UUID] = Query(None, description="Filter by template version"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by rule type, target reference or message"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List validation rules with optional filtering and pagination."""
    items, total = ValidationRuleService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        template_version_id=template_version_id,
        target_type=target_type,
        rule_type=rule_type,
        severity=severity,
        is_active=is_active,
        search=search,
    )
    summaries = [ValidationRuleSummary.model_validate(r) for r in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/validation-rules/{rule_id}", response_model=ValidationRuleResponse)
async def get_validation_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single validation rule by ID."""
    try:
        return ValidationRuleService(db).get(rule_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/validation-rules/{rule_id}", response_model=ValidationRuleResponse)
async def update_validation_rule(
    rule_id: UUID,
    payload: ValidationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing validation rule."""
    try:
        return ValidationRuleService(db).update(
            rule_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/validation-rules/{rule_id}", response_model=MessageResponse)
async def delete_validation_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a validation rule."""
    try:
        ValidationRuleService(db).delete(rule_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Validation rule deleted successfully")


# --- template section rules (scoped read) ---------------------------------- #
@router.get(
    "/template-sections/{section_id}/section-rules",
    response_model=list[SectionRuleSummary],
)
async def list_template_section_rules(
    section_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the section rules (required-document links) for a template section."""
    try:
        TemplateSectionService(db).get(section_id)
    except NotFoundError as exc:
        _handle(exc)
    rules = SectionRuleService(db).list_for_section(section_id)
    return [SectionRuleSummary.model_validate(r) for r in rules]


# --------------------------------------------------------------------------- #
# Section Rules
# --------------------------------------------------------------------------- #
@router.post("/section-rules", response_model=SectionRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_section_rule(
    payload: SectionRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a template section to a required document."""
    try:
        return SectionRuleService(db).create(payload.model_dump(), created_by=_actor(current_user))
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/section-rules", response_model=PaginatedResponse)
async def list_section_rules(
    pagination: PaginationParams = Depends(),
    template_section_id: Optional[UUID] = Query(None, description="Filter by template section"),
    required_document_id: Optional[UUID] = Query(None, description="Filter by required document"),
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List section rules with optional filtering and pagination."""
    items, total = SectionRuleService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        template_section_id=template_section_id,
        required_document_id=required_document_id,
        rule_type=rule_type,
    )
    summaries = [SectionRuleSummary.model_validate(r) for r in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/section-rules/{section_rule_id}", response_model=SectionRuleResponse)
async def get_section_rule(
    section_rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single section rule by ID."""
    try:
        return SectionRuleService(db).get(section_rule_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/section-rules/{section_rule_id}", response_model=SectionRuleResponse)
async def update_section_rule(
    section_rule_id: UUID,
    payload: SectionRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing section rule."""
    try:
        return SectionRuleService(db).update(
            section_rule_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/section-rules/{section_rule_id}", response_model=MessageResponse)
async def delete_section_rule(
    section_rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a section rule."""
    try:
        SectionRuleService(db).delete(section_rule_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Section rule deleted successfully")


# --- submission type profiles (scoped read) -------------------------------- #
@router.get(
    "/submission-types/{submission_type_id}/submission-profiles",
    response_model=list[SubmissionProfileSummary],
)
async def list_submission_type_profiles(
    submission_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the submission profiles defined for a submission type."""
    try:
        SubmissionTypeService(db).get(submission_type_id)
    except NotFoundError as exc:
        _handle(exc)
    profiles = SubmissionProfileService(db).list_for_submission_type(submission_type_id)
    return [SubmissionProfileSummary.model_validate(p) for p in profiles]


@router.get(
    "/submission-profiles/{profile_id}/template-versions",
    response_model=list[TemplateVersionSummary],
)
async def list_submission_profile_template_versions(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the template versions that belong to a submission profile (child records)."""
    try:
        SubmissionProfileService(db).get(profile_id)
    except NotFoundError as exc:
        _handle(exc)
    items, _ = TemplateVersionService(db).list(submission_profile_id=profile_id, limit=10_000)
    return [TemplateVersionSummary.model_validate(tv) for tv in items]


# --------------------------------------------------------------------------- #
# Submission Profiles
# --------------------------------------------------------------------------- #
@router.post("/submission-profiles", response_model=SubmissionProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_submission_profile(
    payload: SubmissionProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new submission profile for a submission type."""
    try:
        return SubmissionProfileService(db).create(
            payload.model_dump(), created_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/submission-profiles", response_model=PaginatedResponse)
async def list_submission_profiles(
    pagination: PaginationParams = Depends(),
    submission_type_id: Optional[UUID] = Query(None, description="Filter by submission type"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List submission profiles with optional filtering and pagination."""
    items, total = SubmissionProfileService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        submission_type_id=submission_type_id,
        is_active=is_active,
        search=search,
    )
    summaries = [SubmissionProfileSummary.model_validate(p) for p in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/submission-profiles/{profile_id}", response_model=SubmissionProfileResponse)
async def get_submission_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single submission profile by ID."""
    try:
        return SubmissionProfileService(db).get(profile_id)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/submission-profiles/{profile_id}", response_model=SubmissionProfileResponse)
async def update_submission_profile(
    profile_id: UUID,
    payload: SubmissionProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing submission profile."""
    try:
        return SubmissionProfileService(db).update(
            profile_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/submission-profiles/{profile_id}", response_model=MessageResponse)
async def delete_submission_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a submission profile."""
    try:
        SubmissionProfileService(db).delete(profile_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Submission profile deleted successfully")
