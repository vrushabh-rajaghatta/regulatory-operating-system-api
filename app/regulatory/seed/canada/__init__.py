"""Canada (Health Canada) ecosystem seed."""

from app.regulatory.seed.framework import Ecosystem
from app.regulatory.seed.canada import (
    master_data,
    configuration,
    submission_profiles,
    templates,
    documents,
    validation,
)

ECOSYSTEM = Ecosystem(
    code="CA",
    name="Canada",
    authority_name="Health Canada",
    master_data=master_data.MASTER_DATA,
    configuration_profiles=configuration.CONFIGURATION_PROFILES,
    submission_profiles=submission_profiles.SUBMISSION_PROFILES,
    structures=templates.STRUCTURES,
    profile_structure=templates.PROFILE_STRUCTURE,
    release_notes=templates.RELEASE_NOTES,
    required_documents=documents.REQUIRED_DOCUMENTS,
    validation_rules=validation.VALIDATION_RULES,
)
