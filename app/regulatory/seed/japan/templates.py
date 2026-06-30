"""Japan — template structure (Summary Technical Documentation, STED)."""

from typing import Any

from app.regulatory.seed.framework import node

# PMDA Summary Technical Documentation (STED), based on the GHTF/IMDRF STED
# format (GHTF/SG1/N011). Clinical evidence (7) is device-conditional.
# SOURCE / VERIFY: MHLW/PMDA STED notifications + GHTF/SG1/N011; reconcile
# against the current PMDA application requirements before treating as
# filing-authoritative.
STRUCTURES: dict[str, list[dict[str, Any]]] = {
    "JP_STED": [
        node("1", "Application Form (Shinsei-sho)", 1),
        node("2", "Device Description and Specifications", 2),
        node("3", "Intended Use / Indications", 3),
        node("4", "Conformity to Essential Principles", 4),
        node("5", "Risk Management", 5),
        node("6", "Nonclinical Studies", 6, children=[
            node("6.1", "Biological Safety", 1),
            node("6.2", "Performance and Stability", 2),
            node("6.3", "Electrical Safety and EMC", 3),
        ]),
        node("7", "Clinical Evidence", 7, required=False),
        node("8", "Labelling and Package Insert (Tenpu Bunsho)", 8),
        node("9", "Quality Management System (QMS)", 9),
    ],
}

PROFILE_STRUCTURE: dict[str, str] = {
    "SHONIN": "JP_STED",
    "NINSHO": "JP_STED",
    "TODOKEDE": "JP_STED",
}

RELEASE_NOTES: dict[str, str] = {
    "JP_STED": "2025.2 — aligned to the PMDA/GHTF STED structure (GHTF/SG1/N011). Pending RA verification.",
}
