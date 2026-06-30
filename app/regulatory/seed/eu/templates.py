"""European Union — template structures (EU MDR & IVDR technical documentation)."""

from typing import Any

from app.regulatory.seed.framework import node

STRUCTURES: dict[str, list[dict[str, Any]]] = {
    # EU MDR (2017/745) technical documentation — Annex II (+ Annex III PMS).
    # Top-level headings confirmed against the EUR-Lex consolidated text of
    # Regulation (EU) 2017/745, Annex II. SOURCE / VERIFY: EUR-Lex CELEX
    # 02017R0745; PMCF (6.4) is device-conditional.
    "EU_MDR_TECH_DOC": [
        node("1", "Device Description and Specification", 1, children=[
            node("1.1", "Device Description and Variants", 1),
            node("1.2", "Intended Purpose and Indications", 2),
        ]),
        node("2", "Information Supplied by the Manufacturer (Labelling and IFU)", 2),
        node("3", "Design and Manufacturing Information", 3),
        node("4", "General Safety and Performance Requirements (GSPR)", 4),
        node("5", "Benefit-Risk Analysis and Risk Management", 5, children=[
            node("5.1", "Benefit-Risk Analysis", 1),
            node("5.2", "Risk Management File", 2),
        ]),
        node("6", "Product Verification and Validation", 6, children=[
            node("6.1", "Preclinical and Clinical Data", 1),
            node("6.2", "Clinical Evaluation Report", 2),
            node("6.3", "Post-Market Surveillance Plan", 3),
            node("6.4", "Post-Market Clinical Follow-up (PMCF)", 4, required=False),
        ]),
    ],
    # EU IVDR (2017/746) technical documentation — Annex II.
    # SOURCE / VERIFY: EUR-Lex CELEX 02017R0746, Annex II. Performance Evaluation
    # (scientific validity / analytical / clinical performance) per Annex XIII;
    # PMPF (6.4) is device-conditional.
    "EU_IVDR_TECH_DOC": [
        node("1", "Device Description and Specification", 1, children=[
            node("1.1", "Device Description and Variants", 1),
            node("1.2", "Intended Purpose", 2),
        ]),
        node("2", "Information Supplied by the Manufacturer (Labelling and IFU)", 2),
        node("3", "Design and Manufacturing Information", 3),
        node("4", "General Safety and Performance Requirements (GSPR)", 4),
        node("5", "Benefit-Risk Analysis and Risk Management", 5),
        node("6", "Performance Evaluation", 6, children=[
            node("6.1", "Scientific Validity", 1),
            node("6.2", "Analytical Performance", 2),
            node("6.3", "Clinical Performance", 3),
            node("6.4", "Post-Market Performance Follow-up (PMPF)", 4, required=False),
        ]),
    ],
}

PROFILE_STRUCTURE: dict[str, str] = {
    "TECH-DOC": "EU_MDR_TECH_DOC",
    "DESIGN-DOSSIER": "EU_MDR_TECH_DOC",
    "IVD-TECH-DOC": "EU_IVDR_TECH_DOC",
}

RELEASE_NOTES: dict[str, str] = {
    "EU_MDR_TECH_DOC": "2025.2 — Annex II headings confirmed against EUR-Lex (Reg. 2017/745). Pending RA verification.",
    "EU_IVDR_TECH_DOC": "2025.2 — aligned to EU IVDR Annex II (Reg. 2017/746). Pending RA verification.",
}
