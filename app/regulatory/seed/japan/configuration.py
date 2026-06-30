"""Japan — PMDA configuration profiles (business behaviour only)."""

from typing import Any

CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "EXPORT": [
        {
            "code": "PMDA_PACKAGE",
            "name": "PMDA Package",
            "version": "1.0",
            "description": "Export packaging for PMDA electronic submissions.",
            "configuration": {
                "package": "zip",
                "compression": True,
                "manifestVersion": "1.0",
                "regionalFormat": "PMDA-eCTD",
                "encoding": "UTF-8",
                "includeChecksums": True,
                "checksumAlgorithm": "sha256",
            },
        },
    ],
    "WORKFLOW": [
        {
            "code": "JAPAN_REVIEW",
            "name": "Japan Review",
            "version": "1.0",
            "description": "Review workflow for PMDA submissions, including expert review.",
            "configuration": {
                "processor": "medical",
                "states": ["Draft", "AI Review", "PMDA Review", "Expert Review", "Approved"],
                "requiresDualApproval": True,
            },
        },
    ],
    "VALIDATION": [
        {
            "code": "PMDA_VALIDATION",
            "name": "PMDA Validation",
            "version": "1.0",
            "description": "Validation behaviour for PMDA submissions.",
            "configuration": {
                "requiredDocuments": True,
                "minimumConfidence": 0.85,
                "enforceMandatorySections": True,
                "languages": ["ja"],
            },
        },
    ],
    "AI_PIPELINE": [
        {
            "code": "PMDA_AI",
            "name": "PMDA AI",
            "version": "1.0",
            "description": "AI processing pipeline for PMDA submissions.",
            "configuration": {
                "steps": [
                    "DocumentClassification",
                    "MetadataExtraction",
                    "Chunking",
                    "EvidenceExtraction",
                    "GapAnalysis",
                    "DraftGeneration",
                ],
                "languages": ["ja", "en"],
                "minimumConfidence": 0.85,
            },
        },
    ],
}
