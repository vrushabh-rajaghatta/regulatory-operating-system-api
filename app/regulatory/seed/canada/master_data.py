"""Canada — Health Canada master data."""

from typing import Any

MASTER_DATA: dict[str, Any] = {
    "country": {"code": "CA", "name": "Canada"},
    "authority": {
        "name": "Health Canada",
        "abbreviation": "HC",
        "website": "https://www.canada.ca/en/health-canada.html",
        "description": "Canada's federal department responsible for health product regulation.",
    },
    "risk_classes": [
        {"code": "CA_CLASS_I", "name": "Class I", "sort_order": 1},
        {"code": "CA_CLASS_II", "name": "Class II", "sort_order": 2},
        {"code": "CA_CLASS_III", "name": "Class III", "sort_order": 3},
        {"code": "CA_CLASS_IV", "name": "Class IV", "sort_order": 4},
    ],
    "regulations": [
        {
            "code": "SOR/98-282",
            "name": "Medical Devices Regulations (SOR/98-282)",
            "description": "Canadian Medical Devices Regulations.",
            "industry": "MEDDEV",
            "risk_class_codes": ["CA_CLASS_I", "CA_CLASS_II", "CA_CLASS_III", "CA_CLASS_IV"],
            "submission_types": [
                {"code": "MDL", "name": "Medical Device Licence", "sequence_prefix": "MDL"},
                {"code": "MDL-AMD", "name": "Medical Device Licence Amendment", "sequence_prefix": "MDL-A"},
                {"code": "MDL-REN", "name": "Medical Device Licence Renewal", "sequence_prefix": "MDL-R"},
                {"code": "PLMDL", "name": "Private Label Medical Device Licence", "sequence_prefix": "PLMDL"},
            ],
        },
    ],
}
