"""Australia — template structures (IMDRF Table of Contents, non-IVD).

The TGA has adopted the IMDRF ToC; this is Australia's own self-contained copy.
"""

from typing import Any

from app.regulatory.seed.framework import node

# The TGA has adopted the IMDRF non-IVD MA Table of Contents. Chapter 1
# (Regional Administrative) is AU-specific; Chapters 2-6 are the harmonised
# IMDRF ToC. SOURCE / VERIFY: IMDRF nIVD MA ToC + TGA IMDRF ToC guidance.
STRUCTURES: dict[str, list[dict[str, Any]]] = {
    "IMDRF_TOC": [
        node("1", "Regional Administrative", 1, description="Region-specific administrative documents.", children=[
            node("1.1", "Application Form", 1),
            node("1.2", "Cover Letter", 2),
            node("1.3", "Comprehensive Device List and Fees", 3),
        ]),
        node("2", "Submission Context", 2, children=[
            node("2.1", "Submission Summary", 1),
            node("2.2", "Device Description and Specification", 2),
            node("2.3", "Indications for Use and Contraindications", 3),
            node("2.4", "Risk Management", 4),
        ]),
        node("3", "Non-Clinical Evidence", 3, children=[
            node("3.1", "Biocompatibility", 1),
            node("3.2", "Sterilization Validation", 2),
            node("3.3", "Software / Firmware Verification and Validation", 3),
            node("3.4", "Electrical Safety and Electromagnetic Compatibility", 4),
            node("3.5", "Bench Performance Testing", 5),
        ]),
        node("4", "Clinical Evidence", 4, children=[
            node("4.1", "Clinical Evaluation / Investigation", 1),
            node("4.2", "Post-Market Clinical Follow-up", 2, required=False),
        ]),
        node("5", "Labelling and Promotional Material", 5, children=[
            node("5.1", "Device Labels", 1),
            node("5.2", "Instructions for Use", 2),
        ]),
        node("6", "Quality Management System", 6, children=[
            node("6.1", "ISO 13485 Certification", 1),
            node("6.2", "Declaration of Conformity", 2),
        ]),
    ],
}

PROFILE_STRUCTURE: dict[str, str] = {
    "ARTG-INCLUSION": "IMDRF_TOC",
    "CONFORMITY-ASSESSMENT": "IMDRF_TOC",
}

RELEASE_NOTES: dict[str, str] = {
    "IMDRF_TOC": "2025.2 — aligned to the IMDRF nIVD MA ToC (TGA regional Chapter 1). Pending RA verification.",
}
