"""United States — template structures (FDA 510(k), PMA, IDE)."""

from typing import Any

from app.regulatory.seed.framework import node

STRUCTURES: dict[str, list[dict[str, Any]]] = {
    # FDA Premarket Notification 510(k) (eSTAR-aligned). Also used for De Novo.
    "FDA_510K": [
        node("1", "Administrative", 1, children=[
            node("1.1", "Medical Device User Fee Cover Sheet (Form FDA 3601)", 1),
            node("1.2", "CDRH Premarket Review Submission Cover Sheet (Form FDA 3514)", 2),
            node("1.3", "510(k) Cover Letter", 3),
        ]),
        node("2", "Indications for Use (Form FDA 3881)", 2),
        node("3", "510(k) Summary or Statement", 3),
        node("4", "Truthful and Accuracy Statement", 4),
        node("5", "Device Description", 5),
        node("6", "Substantial Equivalence Discussion", 6, children=[
            node("6.1", "Predicate Device Comparison", 1),
        ]),
        node("7", "Proposed Labeling", 7),
        node("8", "Performance Testing", 8, children=[
            node("8.1", "Biocompatibility", 1),
            node("8.2", "Sterilization and Shelf Life", 2),
            node("8.3", "Software Documentation", 3),
            node("8.4", "Electromagnetic Compatibility and Electrical Safety", 4),
            node("8.5", "Bench Performance Testing", 5),
            node("8.6", "Clinical Performance", 6, required=False),
        ]),
    ],
    # FDA Premarket Approval (PMA) — modular.
    "FDA_PMA": [
        node("1", "Administrative and Cover Letter", 1),
        node("2", "Summary of Safety and Effectiveness Data", 2),
        node("3", "Device Description and Manufacturing", 3, children=[
            node("3.1", "Device Description", 1),
            node("3.2", "Manufacturing Information", 2),
        ]),
        node("4", "Nonclinical Studies", 4, children=[
            node("4.1", "Biocompatibility", 1),
            node("4.2", "Sterilization", 2),
            node("4.3", "Bench and Animal Testing", 3),
        ]),
        node("5", "Clinical Studies", 5, children=[
            node("5.1", "Study Protocol and Results", 1),
            node("5.2", "Statistical Analysis", 2),
        ]),
        node("6", "Labeling", 6),
        node("7", "Quality System Information", 7),
    ],
    # FDA Investigational Device Exemption (IDE).
    "FDA_IDE": [
        node("1", "Cover Letter and Administrative", 1),
        node("2", "Report of Prior Investigations", 2),
        node("3", "Investigational Plan", 3, children=[
            node("3.1", "Purpose and Protocol", 1),
            node("3.2", "Risk Analysis", 2),
            node("3.3", "Monitoring Procedures", 3),
        ]),
        node("4", "Manufacturing Information", 4),
        node("5", "Investigator Agreements and Certification", 5),
        node("6", "IRB Information and Informed Consent", 6),
        node("7", "Labeling for Investigational Use", 7),
    ],
}

PROFILE_STRUCTURE: dict[str, str] = {
    "510K": "FDA_510K",
    "DE-NOVO": "FDA_510K",
    "PMA": "FDA_PMA",
    "IDE": "FDA_IDE",
}

RELEASE_NOTES: dict[str, str] = {
    "FDA_510K": "Initial 2025.1 release aligned to the FDA 510(k) eSTAR structure.",
    "FDA_PMA": "Initial 2025.1 release aligned to the FDA modular PMA structure.",
    "FDA_IDE": "Initial 2025.1 release aligned to the FDA IDE application structure.",
}
