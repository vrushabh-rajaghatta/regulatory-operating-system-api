"""
Configuration Registry CRUD services.

These services encapsulate the database logic for the configuration registry
entities so the router stays thin. They raise domain exceptions
(`NotFoundError`, `ConflictError`) that the router translates into HTTP
responses.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.configuration.cache import configuration_cache
from app.configuration.models import ConfigurationType, ConfigurationProfile


class ConfigurationError(Exception):
    """Base class for configuration service errors."""


class NotFoundError(ConfigurationError):
    """Raised when a requested entity does not exist."""


class ConflictError(ConfigurationError):
    """Raised when an operation violates a uniqueness/integrity constraint."""


# --------------------------------------------------------------------------- #
# ConfigurationType
# --------------------------------------------------------------------------- #
class ConfigurationTypeService:
    """CRUD operations for ConfigurationType reference data."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, type_id: UUID) -> ConfigurationType:
        config_type = (
            self.db.query(ConfigurationType).filter(ConfigurationType.id == type_id).first()
        )
        if not config_type:
            raise NotFoundError(f"Configuration type not found: {type_id}")
        return config_type

    def get_by_code(self, code: str) -> Optional[ConfigurationType]:
        return (
            self.db.query(ConfigurationType)
            .filter(ConfigurationType.code == code)
            .first()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ConfigurationType], int]:
        query = self.db.query(ConfigurationType)
        if is_active is not None:
            query = query.filter(ConfigurationType.is_active.is_(is_active))
        if search:
            like = f"%{search}%"
            query = query.filter(
                ConfigurationType.name.ilike(like) | ConfigurationType.code.ilike(like)
            )
        total = query.count()
        items = query.order_by(ConfigurationType.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> ConfigurationType:
        code = data.get("code")
        if code and self.get_by_code(code):
            raise ConflictError(f"Configuration type with code '{code}' already exists")
        config_type = ConfigurationType(**data, created_by=created_by, updated_by=created_by)
        self.db.add(config_type)
        self.db.commit()
        self.db.refresh(config_type)
        configuration_cache.clear()  # resolved runtime config may now be stale
        return config_type

    def update(self, type_id: UUID, data: dict, updated_by: Optional[str] = None) -> ConfigurationType:
        config_type = self.get(type_id)
        new_code = data.get("code")
        if new_code and new_code != config_type.code:
            existing = self.get_by_code(new_code)
            if existing and existing.id != config_type.id:
                raise ConflictError(f"Configuration type with code '{new_code}' already exists")
        for field, value in data.items():
            setattr(config_type, field, value)
        if updated_by is not None:
            config_type.updated_by = updated_by
        self.db.commit()
        self.db.refresh(config_type)
        configuration_cache.clear()  # resolved runtime config may now be stale
        return config_type

    def delete(self, type_id: UUID) -> None:
        config_type = self.get(type_id)
        self.db.delete(config_type)
        self.db.commit()
        configuration_cache.clear()  # resolved runtime config may now be stale


# --------------------------------------------------------------------------- #
# ConfigurationProfile
# --------------------------------------------------------------------------- #
class ConfigurationProfileService:
    """CRUD operations for ConfigurationProfile (business config bundles)."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, profile_id: UUID, *, with_type: bool = False) -> ConfigurationProfile:
        query = self.db.query(ConfigurationProfile)
        if with_type:
            query = query.options(joinedload(ConfigurationProfile.configuration_type))
        profile = query.filter(ConfigurationProfile.id == profile_id).first()
        if not profile:
            raise NotFoundError(f"Configuration profile not found: {profile_id}")
        return profile

    def _assert_type_exists(self, configuration_type_id: UUID) -> None:
        if not self.db.query(ConfigurationType.id).filter(
            ConfigurationType.id == configuration_type_id
        ).first():
            raise NotFoundError(f"Configuration type not found: {configuration_type_id}")

    def _key_in_use(
        self,
        configuration_type_id: UUID,
        code: str,
        version: Optional[str],
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        query = self.db.query(ConfigurationProfile.id).filter(
            ConfigurationProfile.configuration_type_id == configuration_type_id,
            ConfigurationProfile.code == code,
            ConfigurationProfile.version.is_(None)
            if version is None
            else ConfigurationProfile.version == version,
        )
        if exclude_id is not None:
            query = query.filter(ConfigurationProfile.id != exclude_id)
        return query.first() is not None

    def list_for_type(self, configuration_type_id: UUID) -> List[ConfigurationProfile]:
        """Return all profiles for a configuration type (unpaginated)."""
        return (
            self.db.query(ConfigurationProfile)
            .filter(ConfigurationProfile.configuration_type_id == configuration_type_id)
            .order_by(ConfigurationProfile.name)
            .all()
        )

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        configuration_type_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ConfigurationProfile], int]:
        query = self.db.query(ConfigurationProfile)
        if configuration_type_id:
            query = query.filter(
                ConfigurationProfile.configuration_type_id == configuration_type_id
            )
        if is_active is not None:
            query = query.filter(ConfigurationProfile.is_active.is_(is_active))
        if search:
            like = f"%{search}%"
            query = query.filter(
                ConfigurationProfile.name.ilike(like) | ConfigurationProfile.code.ilike(like)
            )
        total = query.count()
        items = query.order_by(ConfigurationProfile.name).offset(offset).limit(limit).all()
        return items, total

    def create(self, data: dict, created_by: Optional[str] = None) -> ConfigurationProfile:
        self._assert_type_exists(data["configuration_type_id"])
        if self._key_in_use(
            data["configuration_type_id"], data["code"], data.get("version")
        ):
            raise ConflictError(
                f"Configuration profile with code '{data['code']}' and version "
                f"'{data.get('version')}' already exists for this configuration type"
            )
        profile = ConfigurationProfile(**data, created_by=created_by, updated_by=created_by)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        configuration_cache.clear()  # resolved runtime config may now be stale
        return profile

    def update(self, profile_id: UUID, data: dict, updated_by: Optional[str] = None) -> ConfigurationProfile:
        profile = self.get(profile_id)
        if data.get("configuration_type_id"):
            self._assert_type_exists(data["configuration_type_id"])
        target_type = data.get("configuration_type_id", profile.configuration_type_id)
        target_code = data.get("code", profile.code)
        target_version = data.get("version", profile.version)
        if self._key_in_use(target_type, target_code, target_version, exclude_id=profile.id):
            raise ConflictError(
                f"Configuration profile with code '{target_code}' and version "
                f"'{target_version}' already exists for this configuration type"
            )
        for field, value in data.items():
            setattr(profile, field, value)
        if updated_by is not None:
            profile.updated_by = updated_by
        self.db.commit()
        self.db.refresh(profile)
        configuration_cache.clear()  # resolved runtime config may now be stale
        return profile

    def delete(self, profile_id: UUID) -> None:
        profile = self.get(profile_id)
        self.db.delete(profile)
        self.db.commit()
        configuration_cache.clear()  # resolved runtime config may now be stale
