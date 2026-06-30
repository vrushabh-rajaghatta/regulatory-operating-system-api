"""European Union — submission profiles. IVDR reuses the EU MDR config set."""

SUBMISSION_PROFILES: dict[str, tuple[str, str, str, str]] = {
    "TECH-DOC":       ("EU_MDR_BUNDLE", "EU_MDR_REVIEW", "EU_MDR_VALIDATION", "EU_MDR_AI"),
    "DESIGN-DOSSIER": ("EU_MDR_BUNDLE", "EU_MDR_REVIEW", "EU_MDR_VALIDATION", "EU_MDR_AI"),
    "IVD-TECH-DOC":   ("EU_MDR_BUNDLE", "EU_MDR_REVIEW", "EU_MDR_VALIDATION", "EU_MDR_AI"),
}
