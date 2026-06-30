"""Australia — submission profiles. Workflow reuses the shared STANDARD_REVIEW."""

SUBMISSION_PROFILES: dict[str, tuple[str, str, str, str]] = {
    "ARTG-INCLUSION":        ("TGA_PACKAGE", "STANDARD_REVIEW", "TGA_VALIDATION", "TGA_AI"),
    "CONFORMITY-ASSESSMENT": ("TGA_PACKAGE", "STANDARD_REVIEW", "TGA_VALIDATION", "TGA_AI"),
}
