"""European Union — required documents per template structure."""

from typing import Any

from app.regulatory.seed.framework import doc

REQUIRED_DOCUMENTS: dict[str, list[dict[str, Any]]] = {
    "EU_MDR_TECH_DOC": [
        doc("Device Description", "Device description and specification, including variants and accessories."),
        doc("General Safety and Performance Requirements", "GSPR checklist (Annex I) with evidence of conformity.", extensions=("pdf", "xlsx")),
        doc("Risk Management", "Risk management file per ISO 14971 / Annex I."),
        doc("Clinical Evaluation", "Clinical evaluation report per Annex XIV."),
        doc("Post Market Surveillance", "Post-market surveillance plan and PSUR per Articles 83-86."),
        doc("IFU", "Instructions for use supplied with the device.", extensions=("pdf", "docx")),
        doc("Labelling", "Device labelling and packaging artwork.", extensions=("pdf", "docx")),
        doc("Declaration of Conformity", "EU declaration of conformity per Annex IV."),
        doc("Quality Management Certificate", "ISO 13485 / Annex IX quality management certificate."),
        doc("Post-Market Clinical Follow-up Plan", "PMCF plan per Annex XIV Part B, where applicable.", required=False),
    ],
    "EU_IVDR_TECH_DOC": [
        doc("Device Description", "Device description and specification, including intended purpose."),
        doc("General Safety and Performance Requirements", "GSPR checklist (Annex I) with evidence of conformity.", extensions=("pdf", "xlsx")),
        doc("Risk Management", "Risk management file per ISO 14971 / Annex I."),
        doc("Performance Evaluation Report", "Performance evaluation report per Annex XIII."),
        doc("Scientific Validity Report", "Evidence of the scientific validity of the analyte/marker."),
        doc("Analytical Performance Report", "Analytical performance study data and conclusions.", extensions=("pdf", "xlsx")),
        doc("Clinical Performance Report", "Clinical performance study data and conclusions."),
        doc("IFU", "Instructions for use supplied with the device.", extensions=("pdf", "docx")),
        doc("Labelling", "Device labelling and packaging artwork.", extensions=("pdf", "docx")),
        doc("Declaration of Conformity", "EU declaration of conformity per Annex IV."),
        doc("Post-Market Performance Follow-up Plan", "PMPF plan per Annex XIII Part B, where applicable.", required=False),
    ],
}
