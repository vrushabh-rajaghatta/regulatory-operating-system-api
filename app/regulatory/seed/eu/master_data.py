"""European Union — Notified Body master data."""

from typing import Any

MASTER_DATA: dict[str, Any] = {
    "country": {"code": "EU", "name": "European Union"},
    "authority": {
        "name": "Notified Body",
        "abbreviation": "NB",
        "website": None,
        "description": "Conformity assessment body designated under EU regulations.",
    },
    "risk_classes": [
        {"code": "EU_CLASS_I", "name": "Class I", "sort_order": 1},
        {"code": "EU_CLASS_IIA", "name": "Class IIa", "sort_order": 2},
        {"code": "EU_CLASS_IIB", "name": "Class IIb", "sort_order": 3},
        {"code": "EU_CLASS_III", "name": "Class III", "sort_order": 4},
    ],
    "regulations": [
        {
            "code": "MDR 2017/745",
            "name": "MDR (EU) 2017/745",
            "description": "EU Medical Device Regulation.",
            "industry": "MEDDEV",
            "risk_class_codes": ["EU_CLASS_I", "EU_CLASS_IIA", "EU_CLASS_IIB", "EU_CLASS_III"],
            "submission_types": [
                {"code": "TECH-DOC", "name": "Technical Documentation", "sequence_prefix": "TD"},
                {"code": "DESIGN-DOSSIER", "name": "Design Dossier", "sequence_prefix": "DD"},
            ],
        },
        {
            # Under the IVD industry. The EU risk classes provided (device classes
            # I/IIa/IIb/III) are MDR's; IVDR uses A/B/C/D which were not specified,
            # so its submission type is seeded without a risk-class mapping.
            "code": "IVDR 2017/746",
            "name": "IVDR (EU) 2017/746",
            "description": "EU In Vitro Diagnostic Regulation.",
            "industry": "IVD",
            "risk_class_codes": [],
            "submission_types": [
                {"code": "IVD-TECH-DOC", "name": "Technical Documentation", "sequence_prefix": "IVD-TD"},
            ],
        },
    ],
}
