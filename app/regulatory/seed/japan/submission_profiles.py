"""Japan — submission profiles.

Shonin (approval) uses the full JAPAN_REVIEW workflow; Ninsho/Todokede are
administrative and reuse the shared STANDARD_REVIEW.
"""

SUBMISSION_PROFILES: dict[str, tuple[str, str, str, str]] = {
    "SHONIN":   ("PMDA_PACKAGE", "JAPAN_REVIEW", "PMDA_VALIDATION", "PMDA_AI"),
    "NINSHO":   ("PMDA_PACKAGE", "STANDARD_REVIEW", "PMDA_VALIDATION", "PMDA_AI"),
    "TODOKEDE": ("PMDA_PACKAGE", "STANDARD_REVIEW", "PMDA_VALIDATION", "PMDA_AI"),
}
