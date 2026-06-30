"""Australia — validation rules per template structure (IMDRF ToC)."""

from typing import Any

from app.regulatory.seed.framework import doc_rule, section_rule

VALIDATION_RULES: dict[str, list[dict[str, Any]]] = {
    "IMDRF_TOC": [
        doc_rule("Device Description"),
        doc_rule("Risk Analysis"),
        doc_rule("Instructions for Use"),
        doc_rule("Labels"),
        doc_rule("Declaration of Conformity"),
        doc_rule("Quality Management Certificate"),
        doc_rule("Sterilization Validation", conditional=True),
        doc_rule("Biocompatibility Evaluation", conditional=True),
        section_rule("3", "Non-Clinical Evidence"),
        section_rule("4", "Clinical Evidence"),
    ],
}
