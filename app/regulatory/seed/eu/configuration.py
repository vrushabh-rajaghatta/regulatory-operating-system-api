"""European Union — EU MDR/IVDR configuration profiles (business behaviour only)."""

from typing import Any

CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "EXPORT": [
        {
            "code": "EU_MDR_BUNDLE",
            "name": "EU MDR Bundle",
            "version": "1.0",
            "description": "Export bundle for EU MDR technical documentation.",
            "configuration": {
                "package": "bundle",
                "compression": True,
                "manifestVersion": "3.1",
                "regionalFormat": "EU-MDR",
                "folderStructure": "EU-RPS",
                "includeDeclarationOfConformity": True,
                "language": "multi",
            },
        },
    ],
    "WORKFLOW": [
        {
            "code": "EU_MDR_REVIEW",
            "name": "EU MDR Review",
            "version": "1.0",
            "description": "Review workflow for EU MDR including notified body steps.",
            "configuration": {
                "states": [
                    "Draft",
                    "AI Review",
                    "Clinical Evaluation",
                    "Notified Body Review",
                    "QA",
                    "Approved",
                ],
                "requiresDualApproval": True,
            },
        },
    ],
    "VALIDATION": [
        {
            "code": "EU_MDR_VALIDATION",
            "name": "EU MDR Validation",
            "version": "1.0",
            "description": "Validation behaviour for EU MDR technical documentation.",
            "configuration": {
                "requiredDocuments": True,
                "minimumConfidence": 0.88,
                "requireDeclarationOfConformity": True,
                "requireClinicalEvaluation": True,
            },
        },
    ],
    "AI_PIPELINE": [
        {
            "code": "EU_MDR_AI",
            "name": "EU MDR AI",
            "version": "1.0",
            "description": "AI processing pipeline for EU MDR submissions.",
            "configuration": {
                "steps": [
                    "DocumentClassification",
                    "MetadataExtraction",
                    "Chunking",
                    "EvidenceExtraction",
                    "ClinicalEvidenceMapping",
                    "GapAnalysis",
                    "DraftGeneration",
                ],
                "languages": ["en", "de", "fr"],
                "minimumConfidence": 0.88,
            },
        },
    ],
}
