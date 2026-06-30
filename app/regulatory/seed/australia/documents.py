"""Australia — required documents per template structure (IMDRF ToC)."""

from typing import Any

from app.regulatory.seed.framework import doc

REQUIRED_DOCUMENTS: dict[str, list[dict[str, Any]]] = {
    "IMDRF_TOC": [
        doc("Application Form", "Completed regulatory application form for the device licence.", max_files=1),
        doc("Cover Letter", "Cover letter summarising the submission and contact details."),
        doc("Device Description", "Detailed description of the device, its components, variants and intended use."),
        doc("Risk Analysis", "Risk management file per ISO 14971, including the risk analysis and controls."),
        doc("Instructions for Use", "Directions for use / operator manual provided to the end user.", extensions=("pdf", "docx")),
        doc("Labels", "Device labels, package markings and inserts.", extensions=("pdf", "docx")),
        doc("Declaration of Conformity", "Manufacturer's declaration of conformity to applicable requirements."),
        doc("Quality Management Certificate", "Valid ISO 13485 quality management system certificate."),
        doc("Clinical Evidence Summary", "Summary of clinical evidence supporting safety and effectiveness."),
        doc("Biocompatibility Evaluation", "Biological evaluation report for patient-contacting materials.", required=False),
        doc("Sterilization Validation", "Sterilization process validation report, where applicable.", required=False),
        doc("Software Verification and Validation", "Software lifecycle, verification and validation documentation, where applicable.", required=False),
    ],
}
