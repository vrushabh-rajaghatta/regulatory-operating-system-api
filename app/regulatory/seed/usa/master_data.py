"""United States — FDA master data."""

from typing import Any

MASTER_DATA: dict[str, Any] = {
    "country": {"code": "US", "name": "United States"},
    "authority": {
        "name": "FDA",
        "abbreviation": "FDA",
        "website": "https://www.fda.gov/",
        "description": "United States Food and Drug Administration.",
    },
    "risk_classes": [
        {"code": "US_CLASS_I", "name": "Class I", "sort_order": 1},
        {"code": "US_CLASS_II", "name": "Class II", "sort_order": 2},
        {"code": "US_CLASS_III", "name": "Class III", "sort_order": 3},
    ],
    "regulations": [
        {
            # Establishment registration, device listing & premarket notification.
            "code": "21 CFR 807",
            "name": "21 CFR Part 807",
            "description": "Establishment Registration and Device Listing; Premarket Notification.",
            "industry": "MEDDEV",
            "risk_class_codes": ["US_CLASS_I", "US_CLASS_II", "US_CLASS_III"],
            "submission_types": [
                {"code": "510K", "name": "510(k)", "sequence_prefix": "K"},
                {"code": "DE-NOVO", "name": "De Novo", "sequence_prefix": "DEN"},
            ],
        },
        {
            # Premarket approval. IDE (formally 21 CFR 812) is grouped here under
            # the premarket-pathway regulation provided.
            "code": "21 CFR 814",
            "name": "21 CFR Part 814",
            "description": "Premarket Approval of Medical Devices.",
            "industry": "MEDDEV",
            "risk_class_codes": ["US_CLASS_I", "US_CLASS_II", "US_CLASS_III"],
            "submission_types": [
                {"code": "PMA", "name": "PMA", "sequence_prefix": "P"},
                {"code": "IDE", "name": "IDE", "sequence_prefix": "G"},
            ],
        },
    ],
}
