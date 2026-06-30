"""Australia — TGA master data."""

from typing import Any

MASTER_DATA: dict[str, Any] = {
    "country": {"code": "AU", "name": "Australia"},
    "authority": {
        "name": "TGA",
        "abbreviation": "TGA",
        "website": "https://www.tga.gov.au/",
        "description": "Australian Therapeutic Goods Administration.",
    },
    "risk_classes": [
        {"code": "AU_CLASS_I", "name": "Class I", "sort_order": 1},
        {"code": "AU_CLASS_IIA", "name": "Class IIa", "sort_order": 2},
        {"code": "AU_CLASS_IIB", "name": "Class IIb", "sort_order": 3},
        {"code": "AU_CLASS_III", "name": "Class III", "sort_order": 4},
    ],
    "regulations": [
        {
            "code": "TG Act 1989",
            "name": "Therapeutic Goods Act",
            "description": "Australian Therapeutic Goods Act.",
            "industry": "MEDDEV",
            "risk_class_codes": ["AU_CLASS_I", "AU_CLASS_IIA", "AU_CLASS_IIB", "AU_CLASS_III"],
            "submission_types": [
                {"code": "ARTG-INCLUSION", "name": "ARTG Inclusion", "sequence_prefix": "ARTG"},
                {"code": "CONFORMITY-ASSESSMENT", "name": "Conformity Assessment", "sequence_prefix": "CA"},
            ],
        },
    ],
}
