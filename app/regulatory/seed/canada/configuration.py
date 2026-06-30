"""Canada — Health Canada configuration profiles (business behaviour only)."""

from typing import Any

CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "EXPORT": [
        {
            "code": "HEALTH_CANADA_ZIP",
            "name": "Health Canada ZIP",
            "version": "1.0",
            "description": "Export packaging for Health Canada electronic submissions.",
            "configuration": {
                "package": "zip",
                "compression": True,
                "manifestVersion": "2.0",
                "regionalFormat": "HC-RPS",
                "folderStructure": "eCTD",
                "includeChecksums": True,
                "checksumAlgorithm": "sha256",
            },
        },
    ],
    "WORKFLOW": [
        {
            "code": "HEALTH_CANADA_REVIEW",
            "name": "Health Canada Review",
            "version": "1.0",
            "description": "Review workflow for Health Canada medical device submissions.",
            "configuration": {
                "processor": "medical",
                "states": ["Draft", "AI Review", "Medical Review", "QA", "Approved"],
                "requiresDualApproval": True,
            },
        },
    ],
    "VALIDATION": [
        {
            "code": "HEALTH_CANADA_VALIDATION",
            "name": "Health Canada Validation",
            "version": "1.0",
            "description": "Validation behaviour for Health Canada submissions.",
            "configuration": {
                "processor": "bilingual",
                "requiredDocuments": True,
                "minimumConfidence": 0.85,
                "enforceMandatorySections": True,
                "languages": ["en", "fr"],
            },
        },
    ],
    "AI_PIPELINE": [
        {
            "code": "HEALTH_CANADA_AI",
            "name": "Health Canada AI",
            "version": "1.0",
            "description": "AI processing pipeline for Health Canada submissions.",
            "configuration": {
                "steps": [
                    "DocumentClassification",
                    "MetadataExtraction",
                    "Chunking",
                    "EvidenceExtraction",
                    "GapAnalysis",
                    "DraftGeneration",
                ],
                "languages": ["en", "fr"],
                "minimumConfidence": 0.85,
            },
        },
    ],
}
