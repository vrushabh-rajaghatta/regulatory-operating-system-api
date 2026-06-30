"""European Union — validation rules per template structure."""

from typing import Any

from app.regulatory.seed.framework import doc_rule, section_rule

VALIDATION_RULES: dict[str, list[dict[str, Any]]] = {
    "EU_MDR_TECH_DOC": [
        doc_rule("General Safety and Performance Requirements"),
        doc_rule("Clinical Evaluation"),
        doc_rule("Risk Management"),
        doc_rule("Post Market Surveillance"),
        doc_rule("IFU"),
        doc_rule("Labelling"),
        doc_rule("Declaration of Conformity"),
        doc_rule("Post-Market Clinical Follow-up Plan", conditional=True),
        section_rule("4", "General Safety and Performance Requirements (GSPR)"),
        section_rule("6", "Product Verification and Validation"),
    ],
    "EU_IVDR_TECH_DOC": [
        doc_rule("General Safety and Performance Requirements"),
        doc_rule("Performance Evaluation Report"),
        doc_rule("Scientific Validity Report"),
        doc_rule("Analytical Performance Report"),
        doc_rule("Clinical Performance Report"),
        doc_rule("Risk Management"),
        doc_rule("Declaration of Conformity"),
        doc_rule("Post-Market Performance Follow-up Plan", conditional=True),
        section_rule("6", "Performance Evaluation"),
    ],
}
