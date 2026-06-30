"""United States — validation rules per template structure."""

from typing import Any

from app.regulatory.seed.framework import doc_rule, section_rule

VALIDATION_RULES: dict[str, list[dict[str, Any]]] = {
    "FDA_510K": [
        doc_rule("Cover Letter"),
        doc_rule("Indications for Use"),
        doc_rule("Device Description"),
        doc_rule("Predicate Device Information"),
        doc_rule("Performance Testing"),
        doc_rule("Labelling"),
        doc_rule("Sterilization Information", conditional=True),
        doc_rule("Software Documentation", conditional=True),
        doc_rule("Biocompatibility", conditional=True),
        section_rule("6", "Substantial Equivalence Discussion"),
    ],
    "FDA_PMA": [
        doc_rule("Summary of Safety and Effectiveness Data"),
        doc_rule("Device Description"),
        doc_rule("Manufacturing Information"),
        doc_rule("Nonclinical Studies"),
        doc_rule("Clinical Investigation Report"),
        doc_rule("Proposed Labeling"),
        doc_rule("Quality System Information"),
        section_rule("5", "Clinical Studies"),
    ],
    "FDA_IDE": [
        doc_rule("Report of Prior Investigations"),
        doc_rule("Investigational Plan"),
        doc_rule("Risk Analysis"),
        doc_rule("IRB Approval"),
        doc_rule("Informed Consent Form"),
        doc_rule("Investigational Device Labeling"),
        section_rule("3", "Investigational Plan"),
    ],
}
