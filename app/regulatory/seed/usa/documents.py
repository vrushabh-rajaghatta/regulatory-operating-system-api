"""United States — required documents per template structure."""

from typing import Any

from app.regulatory.seed.framework import doc

REQUIRED_DOCUMENTS: dict[str, list[dict[str, Any]]] = {
    "FDA_510K": [
        doc("Cover Letter", "510(k) cover letter identifying the submission and the submitter."),
        doc("Indications for Use", "Indications for Use statement (Form FDA 3881)."),
        doc("510(k) Summary", "510(k) summary or statement per 21 CFR 807.92/807.93."),
        doc("Device Description", "Description of the device, principles of operation and technological characteristics."),
        doc("Predicate Device Information", "Identification of the predicate device(s) relied upon for substantial equivalence."),
        doc("Substantial Equivalence Comparison", "Comparison of the subject and predicate devices supporting substantial equivalence."),
        doc("Performance Testing", "Bench performance test protocols and results.", extensions=("pdf", "xlsx")),
        doc("Software Documentation", "Software/firmware documentation per FDA guidance, where applicable.", required=False),
        doc("Sterilization Information", "Sterilization method and validation, where applicable.", required=False),
        doc("Biocompatibility", "Biocompatibility evaluation for patient-contacting components, where applicable.", required=False),
        doc("Labelling", "Proposed labelling, including packaging and instructions for use.", extensions=("pdf", "docx")),
        doc("Truthful and Accuracy Statement", "Signed truthful and accuracy statement per 21 CFR 807.87(k)."),
    ],
    "FDA_PMA": [
        doc("Cover Letter", "PMA cover letter and table of contents."),
        doc("Summary of Safety and Effectiveness Data", "SSED summarising nonclinical and clinical evidence."),
        doc("Device Description", "Complete device description, components and principles of operation."),
        doc("Manufacturing Information", "Manufacturing methods, facilities and controls."),
        doc("Nonclinical Studies", "Nonclinical laboratory study reports (bench and animal).", extensions=("pdf", "xlsx")),
        doc("Clinical Investigation Report", "Clinical study protocol, data and results."),
        doc("Statistical Analysis", "Statistical analysis plan and results for the clinical data.", extensions=("pdf", "xlsx")),
        doc("Proposed Labeling", "Proposed labeling, including the indications and directions for use.", extensions=("pdf", "docx")),
        doc("Quality System Information", "Quality system information and conformance evidence."),
        doc("Biocompatibility Evaluation", "Biological evaluation report for patient-contacting materials.", required=False),
    ],
    "FDA_IDE": [
        doc("Cover Letter", "IDE cover letter and administrative information."),
        doc("Report of Prior Investigations", "Report of prior clinical, animal and laboratory investigations."),
        doc("Investigational Plan", "Investigational plan including purpose, protocol and study design."),
        doc("Risk Analysis", "Risk analysis describing risks to subjects and mitigations."),
        doc("Manufacturing Information", "Description of manufacturing methods and controls for the investigational device."),
        doc("Investigator Agreement", "Signed investigator agreements and certifications."),
        doc("IRB Approval", "Documentation of Institutional Review Board approval."),
        doc("Informed Consent Form", "Informed consent form provided to study subjects.", extensions=("pdf", "docx")),
        doc("Investigational Device Labeling", "Labeling bearing the investigational-use statement.", extensions=("pdf", "docx")),
        doc("Monitoring Plan", "Plan for monitoring the clinical investigation.", required=False),
    ],
}
