"""Japan — validation rules per template structure (STED)."""

from typing import Any

from app.regulatory.seed.framework import doc_rule, section_rule

VALIDATION_RULES: dict[str, list[dict[str, Any]]] = {
    "JP_STED": [
        doc_rule("Application Form (Shinsei-sho)"),
        doc_rule("Device Description and Specifications"),
        doc_rule("Conformity to Essential Principles"),
        doc_rule("Risk Management Report"),
        doc_rule("Nonclinical Test Reports"),
        doc_rule("Package Insert (Tenpu Bunsho)"),
        doc_rule("QMS Conformity Certificate"),
        doc_rule("Clinical Evidence", conditional=True),
        section_rule("4", "Conformity to Essential Principles"),
    ],
}
