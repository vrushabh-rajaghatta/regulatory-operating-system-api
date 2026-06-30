"""United States — FDA configuration profiles (business behaviour only)."""

from typing import Any

CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "EXPORT": [
        {
            "code": "FDA_ECOPY",
            "name": "FDA eCopy",
            "version": "1.0",
            "description": "Export packaging conforming to the FDA eCopy program.",
            "configuration": {
                "package": "ecopy",
                "compression": False,
                "manifestVersion": "1.0",
                "mediaType": "electronic",
                "volumeStructure": "eCopy",
                "includeChecksums": True,
                "checksumAlgorithm": "md5",
            },
        },
    ],
    "WORKFLOW": [
        {
            "code": "FDA_REVIEW",
            "name": "FDA Review",
            "version": "1.0",
            "description": "Review workflow aligned to FDA submission gating.",
            "configuration": {
                "states": [
                    "Draft",
                    "AI Review",
                    "Scientific Review",
                    "Compliance Review",
                    "QA",
                    "Approved",
                    "Submitted",
                ],
                "requiresDualApproval": True,
            },
        },
    ],
    "VALIDATION": [
        {
            "code": "FDA_VALIDATION",
            "name": "FDA Validation",
            "version": "1.0",
            "description": "Validation behaviour for FDA submissions.",
            "configuration": {
                "requiredDocuments": True,
                "minimumConfidence": 0.9,
                "enforceMandatorySections": True,
                "blockOnError": True,
            },
        },
    ],
    "AI_PIPELINE": [
        {
            "code": "FDA_AI",
            "name": "FDA AI",
            "version": "1.0",
            "description": "AI processing pipeline for FDA submissions.",
            "configuration": {
                "steps": [
                    "DocumentClassification",
                    "MetadataExtraction",
                    "Chunking",
                    "EvidenceExtraction",
                    "GapAnalysis",
                    "DraftGeneration",
                    "ComplianceCheck",
                ],
                "languages": ["en"],
                "minimumConfidence": 0.9,
            },
        },
    ],
}
