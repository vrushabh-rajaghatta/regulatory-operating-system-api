"""Canada — submission profiles: submission type -> (export, workflow, validation, ai)."""

# Renewals / private-label are administrative, so they use the shared STANDARD_REVIEW.
SUBMISSION_PROFILES: dict[str, tuple[str, str, str, str]] = {
    "MDL":     ("HEALTH_CANADA_ZIP", "HEALTH_CANADA_REVIEW", "HEALTH_CANADA_VALIDATION", "HEALTH_CANADA_AI"),
    "MDL-AMD": ("HEALTH_CANADA_ZIP", "HEALTH_CANADA_REVIEW", "HEALTH_CANADA_VALIDATION", "HEALTH_CANADA_AI"),
    "MDL-REN": ("HEALTH_CANADA_ZIP", "STANDARD_REVIEW", "HEALTH_CANADA_VALIDATION", "HEALTH_CANADA_AI"),
    "PLMDL":   ("HEALTH_CANADA_ZIP", "STANDARD_REVIEW", "HEALTH_CANADA_VALIDATION", "HEALTH_CANADA_AI"),
}
