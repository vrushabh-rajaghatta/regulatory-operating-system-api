"""
Central models import module.

This module imports all SQLAlchemy models to ensure they are registered
with the Base metadata for proper table creation and relationships.
"""

# Import all models to register them with SQLAlchemy
from app.projects.models import Project
from app.products.models import Product
from app.submissions.models import Submission, SubmissionDocument, SubmissionValidationItem
from app.dossier.models import DossierSection, section_content_association
from app.files.models import UploadedFile, ExtractedContent
from app.reviews.models import HumanReview
from app.validation.models import MissingContent, ConsistencyCheck
from app.auth.models import Organization, User
from app.regulatory.models import (
    Country, Authority, Industry, Regulation, SubmissionType, SubmissionProfile,
    RiskClassification, submission_type_risk_class, TemplateVersion, TemplateSection,
    RequiredDocument, ValidationRule, SectionRule,
)
from app.configuration.models import ConfigurationType, ConfigurationProfile

# Export all models for easy importing
__all__ = [
    "Project",
    "Product",
    "Submission",
    "SubmissionDocument",
    "SubmissionValidationItem",
    "DossierSection",
    "UploadedFile",
    "ExtractedContent",
    "HumanReview",
    "MissingContent",
    "ConsistencyCheck",
    "section_content_association",
    "Organization",
    "User",
    "Country",
    "Authority",
    "Industry",
    "Regulation",
    "SubmissionType",
    "SubmissionProfile",
    "RiskClassification",
    "submission_type_risk_class",
    "TemplateVersion",
    "TemplateSection",
    "RequiredDocument",
    "ValidationRule",
    "SectionRule",
    "ConfigurationType",
    "ConfigurationProfile",
]