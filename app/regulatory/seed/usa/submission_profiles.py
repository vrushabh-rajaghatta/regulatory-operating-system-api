"""United States — submission profiles. All FDA pathways share the FDA config set."""

SUBMISSION_PROFILES: dict[str, tuple[str, str, str, str]] = {
    "510K":    ("FDA_ECOPY", "FDA_REVIEW", "FDA_VALIDATION", "FDA_AI"),
    "DE-NOVO": ("FDA_ECOPY", "FDA_REVIEW", "FDA_VALIDATION", "FDA_AI"),
    "PMA":     ("FDA_ECOPY", "FDA_REVIEW", "FDA_VALIDATION", "FDA_AI"),
    "IDE":     ("FDA_ECOPY", "FDA_REVIEW", "FDA_VALIDATION", "FDA_AI"),
}
