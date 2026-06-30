"""
Configuration Registry models.

Global (not organization-scoped) reference entities for storing reusable
business configurations:

    ConfigurationType 1---* ConfigurationProfile

The ``configuration`` JSON on a profile stores BUSINESS configuration only.
It must never contain implementation class names, Python module names or
service names — those are resolved in code, not persisted as data.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, ForeignKey, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.models import BaseModel, AuditMixin


class ConfigurationType(BaseModel, AuditMixin):
    """
    A category of reusable business configuration (e.g. EXPORT, WORKFLOW,
    VALIDATION, AI_PIPELINE).

    Parent of one or more configuration profiles.
    """

    __tablename__ = "configuration_types"

    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    profiles = relationship(
        "ConfigurationProfile",
        back_populates="configuration_type",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ConfigurationType(id={self.id}, code='{self.code}', name='{self.name}')>"


class ConfigurationProfile(BaseModel, AuditMixin):
    """
    A named, versioned bundle of business configuration belonging to a
    ConfigurationType.

    The ``configuration`` column stores BUSINESS configuration only (thresholds,
    toggles, ordered steps, language sets, etc.). It deliberately does NOT store
    implementation class names, module names or service names.
    """

    __tablename__ = "configuration_profiles"
    __table_args__ = (
        UniqueConstraint(
            "configuration_type_id",
            "code",
            "version",
            name="uq_configuration_profiles_type_code_version",
        ),
    )

    configuration_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("configuration_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True, index=True)
    # Business configuration only — never implementation/class/module/service names.
    configuration = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    configuration_type = relationship("ConfigurationType", back_populates="profiles")

    def __repr__(self) -> str:
        return (
            f"<ConfigurationProfile(id={self.id}, code='{self.code}', "
            f"version='{self.version}', configuration_type={self.configuration_type_id})>"
        )
