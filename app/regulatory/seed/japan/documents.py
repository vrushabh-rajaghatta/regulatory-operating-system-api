"""Japan — required documents per template structure (STED)."""

from typing import Any

from app.regulatory.seed.framework import doc

REQUIRED_DOCUMENTS: dict[str, list[dict[str, Any]]] = {
    "JP_STED": [
        doc("Application Form (Shinsei-sho)", "Completed PMDA application form."),
        doc("Device Description and Specifications", "Description of the device, specifications and intended use."),
        doc("STED Summary", "Summary Technical Documentation overview."),
        doc("Conformity to Essential Principles", "Checklist demonstrating conformity to the Essential Principles.", extensions=("pdf", "xlsx")),
        doc("Risk Management Report", "Risk management report per ISO 14971 / JIS T 14971."),
        doc("Nonclinical Test Reports", "Nonclinical test reports (biological safety, performance, electrical safety).", extensions=("pdf", "xlsx")),
        doc("Package Insert (Tenpu Bunsho)", "Package insert / instructions for use.", extensions=("pdf", "docx")),
        doc("Device Labelling", "Device labelling and packaging.", extensions=("pdf", "docx")),
        doc("QMS Conformity Certificate", "Evidence of QMS conformity (ISO 13485 / MHLW Ordinance 169)."),
        doc("Clinical Evidence", "Clinical evidence, where required by device class.", required=False),
    ],
}
