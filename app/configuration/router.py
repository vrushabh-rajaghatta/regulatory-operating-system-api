"""
Configuration Registry API router.

Exposes full CRUD for the configuration registry entities:
    /configuration-types, /configuration-profiles

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
from app.configuration.services import (
    ConfigurationTypeService,
    ConfigurationProfileService,
    NotFoundError,
    ConflictError,
)
from app.configuration.schemas import (
    ConfigurationTypeCreate,
    ConfigurationTypeUpdate,
    ConfigurationTypeResponse,
    ConfigurationTypeSummary,
    ConfigurationProfileCreate,
    ConfigurationProfileUpdate,
    ConfigurationProfileResponse,
    ConfigurationProfileSummary,
)

router = APIRouter()


def _actor(current_user: User) -> str:
    """Identify the acting user for audit fields."""
    return current_user.username


def _handle(error: Exception):
    """Translate a configuration service error into an HTTPException."""
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    raise error


# --------------------------------------------------------------------------- #
# Configuration Types
# --------------------------------------------------------------------------- #
@router.post(
    "/configuration-types",
    response_model=ConfigurationTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_configuration_type(
    payload: ConfigurationTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new configuration type."""
    try:
        return ConfigurationTypeService(db).create(
            payload.model_dump(), created_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/configuration-types", response_model=PaginatedResponse)
async def list_configuration_types(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List configuration types with optional filtering and pagination."""
    items, total = ConfigurationTypeService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        is_active=is_active,
        search=search,
    )
    summaries = [ConfigurationTypeSummary.model_validate(t) for t in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/configuration-types/{type_id}", response_model=ConfigurationTypeResponse)
async def get_configuration_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single configuration type by ID."""
    try:
        config_type = ConfigurationTypeService(db).get(type_id)
    except NotFoundError as exc:
        _handle(exc)
    config_type.profiles_count = len(config_type.profiles)
    return config_type


@router.put("/configuration-types/{type_id}", response_model=ConfigurationTypeResponse)
async def update_configuration_type(
    type_id: UUID,
    payload: ConfigurationTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing configuration type."""
    try:
        return ConfigurationTypeService(db).update(
            type_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/configuration-types/{type_id}", response_model=MessageResponse)
async def delete_configuration_type(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a configuration type (cascades to its profiles)."""
    try:
        ConfigurationTypeService(db).delete(type_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Configuration type deleted successfully")


# --- configuration type profiles (scoped read) ----------------------------- #
@router.get(
    "/configuration-types/{type_id}/configuration-profiles",
    response_model=list[ConfigurationProfileSummary],
)
async def list_configuration_type_profiles(
    type_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the configuration profiles defined for a configuration type."""
    try:
        ConfigurationTypeService(db).get(type_id)
    except NotFoundError as exc:
        _handle(exc)
    profiles = ConfigurationProfileService(db).list_for_type(type_id)
    return [ConfigurationProfileSummary.model_validate(p) for p in profiles]


# --------------------------------------------------------------------------- #
# Configuration Profiles
# --------------------------------------------------------------------------- #
@router.post(
    "/configuration-profiles",
    response_model=ConfigurationProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_configuration_profile(
    payload: ConfigurationProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new configuration profile for a configuration type."""
    try:
        return ConfigurationProfileService(db).create(
            payload.model_dump(), created_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.get("/configuration-profiles", response_model=PaginatedResponse)
async def list_configuration_profiles(
    pagination: PaginationParams = Depends(),
    configuration_type_id: Optional[UUID] = Query(None, description="Filter by configuration type"),
    is_active: Optional[bool] = Query(None, description="Filter by active flag"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List configuration profiles with optional filtering and pagination."""
    items, total = ConfigurationProfileService(db).list(
        offset=pagination.offset,
        limit=pagination.limit,
        configuration_type_id=configuration_type_id,
        is_active=is_active,
        search=search,
    )
    summaries = [ConfigurationProfileSummary.model_validate(p) for p in items]
    return PaginatedResponse.create(items=summaries, total=total, pagination=pagination)


@router.get("/configuration-profiles/{profile_id}", response_model=ConfigurationProfileResponse)
async def get_configuration_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single configuration profile by ID."""
    try:
        return ConfigurationProfileService(db).get(profile_id, with_type=True)
    except NotFoundError as exc:
        _handle(exc)


@router.put("/configuration-profiles/{profile_id}", response_model=ConfigurationProfileResponse)
async def update_configuration_profile(
    profile_id: UUID,
    payload: ConfigurationProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing configuration profile."""
    try:
        return ConfigurationProfileService(db).update(
            profile_id, payload.model_dump(exclude_unset=True), updated_by=_actor(current_user)
        )
    except (NotFoundError, ConflictError) as exc:
        _handle(exc)


@router.delete("/configuration-profiles/{profile_id}", response_model=MessageResponse)
async def delete_configuration_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a configuration profile."""
    try:
        ConfigurationProfileService(db).delete(profile_id)
    except NotFoundError as exc:
        _handle(exc)
    return MessageResponse(message="Configuration profile deleted successfully")
