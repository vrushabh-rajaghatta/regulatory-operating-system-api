"""Japan — PMDA master data."""

from typing import Any

MASTER_DATA: dict[str, Any] = {
    "country": {"code": "JP", "name": "Japan"},
    "authority": {
        "name": "PMDA",
        "abbreviation": "PMDA",
        "website": "https://www.pmda.go.jp/english/",
        "description": "Japanese Pharmaceuticals and Medical Devices Agency.",
    },
    "risk_classes": [
        {"code": "JP_CLASS_I", "name": "Class I", "sort_order": 1},
        {"code": "JP_CLASS_II", "name": "Class II", "sort_order": 2},
        {"code": "JP_CLASS_III", "name": "Class III", "sort_order": 3},
        {"code": "JP_CLASS_IV", "name": "Class IV", "sort_order": 4},
    ],
    "regulations": [
        {
            "code": "PMD Act",
            "name": "PMD Act",
            "description": "Japanese Pharmaceuticals and Medical Devices Act.",
            "industry": "MEDDEV",
            "risk_class_codes": ["JP_CLASS_I", "JP_CLASS_II", "JP_CLASS_III", "JP_CLASS_IV"],
            "submission_types": [
                {"code": "SHONIN", "name": "Shonin", "sequence_prefix": "SHO"},
                {"code": "NINSHO", "name": "Ninsho", "sequence_prefix": "NIN"},
                {"code": "TODOKEDE", "name": "Todokede", "sequence_prefix": "TOD"},
            ],
        },
    ],
}
