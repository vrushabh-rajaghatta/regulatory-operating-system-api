"""
Configuration Registry schemas for API request/response validation.
"""

from pydantic import Field
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.core.schemas import BaseSchema, TimestampSchema, UUIDSchema


# --------------------------------------------------------------------------- #
# ConfigurationType
# --------------------------------------------------------------------------- #
class ConfigurationTypeBase(BaseSchema):
    """Base configuration type schema with common fields."""

    code: str = Field(..., min_length=1, max_length=100, description="Configuration type code, e.g. 'EXPORT'")
    name: str = Field(..., min_length=1, max_length=255, description="Configuration type name")
    description: Optional[str] = Field(None, description="Configuration type description")
    is_active: bool = Field(default=True, description="Whether the configuration type is active")


class ConfigurationTypeCreate(ConfigurationTypeBase):
    """Schema for creating a new configuration type."""


class ConfigurationTypeUpdate(BaseSchema):
    """Schema for updating an existing configuration type."""

    code: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigurationTypeSummary(UUIDSchema):
    """Lightweight configuration type reference for lists and nesting."""

    code: str
    name: str
    is_active: bool


class ConfigurationTypeResponse(ConfigurationTypeBase, UUIDSchema, TimestampSchema):
    """Schema for configuration type API responses."""

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    profiles_count: Optional[int] = Field(
        None, description="Number of configuration profiles under this type"
    )


# --------------------------------------------------------------------------- #
# ConfigurationProfile
# --------------------------------------------------------------------------- #
class ConfigurationProfileBase(BaseSchema):
    """Base configuration profile schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    code: str = Field(..., min_length=1, max_length=100, description="Profile code")
    description: Optional[str] = Field(None, description="Profile description")
    version: Optional[str] = Field(None, max_length=50, description="Profile version label")
    configuration: Optional[Dict[str, Any]] = Field(
        None,
        description="Business configuration only — no class/module/service names",
    )
    is_active: bool = Field(default=True, description="Whether the profile is active")


class ConfigurationProfileCreate(ConfigurationProfileBase):
    """Schema for creating a new configuration profile."""

    configuration_type_id: UUID = Field(..., description="Owning configuration type ID")


class ConfigurationProfileUpdate(BaseSchema):
    """Schema for updating an existing configuration profile."""

    configuration_type_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, max_length=50)
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConfigurationProfileSummary(UUIDSchema):
    """Lightweight configuration profile reference for lists."""

    configuration_type_id: UUID
    name: str
    code: str
    version: Optional[str] = None
    is_active: bool


class ConfigurationProfileResponse(ConfigurationProfileBase, UUIDSchema, TimestampSchema):
    """Schema for configuration profile API responses."""

    configuration_type_id: UUID
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    configuration_type: Optional[ConfigurationTypeSummary] = None
