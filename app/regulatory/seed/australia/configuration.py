"""Australia — TGA configuration profiles (business behaviour only).

No TGA-specific workflow is defined; ARTG submissions use the shared
STANDARD_REVIEW workflow (see common.py).
"""

from typing import Any

CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "EXPORT": [
        {
            "code": "TGA_PACKAGE",
            "name": "TGA Package",
            "version": "1.0",
            "description": "Export packaging for TGA electronic submissions.",
            "configuration": {
                "package": "zip",
                "compression": True,
                "manifestVersion": "1.5",
                "regionalFormat": "TGA-eSubmission",
                "dossierType": "CTD",
                "includeChecksums": True,
            },
        },
    ],
    "VALIDATION": [
        {
            "code": "TGA_VALIDATION",
            "name": "TGA Validation",
            "version": "1.0",
            "description": "Validation behaviour for TGA submissions.",
            "configuration": {
                "requiredDocuments": True,
                "minimumConfidence": 0.8,
                "enforceMandatorySections": True,
            },
        },
    ],
    "AI_PIPELINE": [
        {
            "code": "TGA_AI",
            "name": "TGA AI",
            "version": "1.0",
            "description": "AI processing pipeline for TGA submissions.",
            "configuration": {
                "steps": [
                    "DocumentClassification",
                    "MetadataExtraction",
                    "Chunking",
                    "EvidenceExtraction",
                    "GapAnalysis",
                    "DraftGeneration",
                ],
                "languages": ["en"],
                "minimumConfidence": 0.82,
            },
        },
    ],
}
