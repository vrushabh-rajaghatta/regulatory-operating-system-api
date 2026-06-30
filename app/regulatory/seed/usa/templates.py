"""United States — template structures (FDA 510(k), PMA, IDE)."""

from typing import Any

from app.regulatory.seed.framework import node

STRUCTURES: dict[str, list[dict[str, Any]]] = {
    # FDA Premarket Notification 510(k) — aligned to the FDA eSTAR template
    # (mandatory for 510(k)s since 1 Oct 2023). Also used for De Novo.
    #
    # Top-level sections mirror the eSTAR interactive PDF's section set. Sections
    # eSTAR shows conditionally — based on device characteristics (sterile,
    # reusable, software, electrical, patient-contacting, animal/clinical data) —
    # are marked required=False here.
    #
    # SOURCE / VERIFY: reconcile against the live eSTAR template and FDA guidance
    # "Electronic Submission Template for Medical Device 510(k) Submissions"
    # (fda.gov/media/152429) and "Content of a 510(k)". fda.gov blocks automated
    # fetch, so an RA reviewer should confirm section labels/order against the
    # current eSTAR PDF before this is treated as filing-authoritative.
    "FDA_510K": [
        node("1", "Administrative Information", 1, children=[
            node("1.1", "510(k) Cover Letter", 1),
            node("1.2", "Medical Device User Fee Cover Sheet (Form FDA 3601)", 2),
            node("1.3", "CDRH Premarket Review Submission Cover Sheet (Form FDA 3514)", 3),
            node("1.4", "Submitter / Applicant and US Agent Information", 4),
        ]),
        node("2", "Pre-Submission Correspondence and Previous Regulator Interaction", 2, required=False),
        node("3", "Consensus Standards", 3),
        node("4", "Device Description", 4),
        node("5", "Proposed Indications for Use (Form FDA 3881)", 5),
        node("6", "Classification", 6),
        node("7", "Predicates and Substantial Equivalence", 7, children=[
            node("7.1", "Predicate Device Identification", 1),
            node("7.2", "Substantial Equivalence Comparison", 2),
        ]),
        node("8", "Design / Special Controls, Guidance Documents, and Risk to Health", 8),
        node("9", "Labeling", 9),
        node("10", "Reprocessing", 10, required=False),
        node("11", "Sterility", 11, required=False),
        node("12", "Shelf Life", 12, required=False),
        node("13", "Biocompatibility", 13, required=False),
        node("14", "Software / Firmware (Device Software Functions)", 14, required=False),
        node("15", "Cybersecurity / Interoperability", 15, required=False),
        node("16", "Electromagnetic Compatibility, Wireless, Electrical, Mechanical and Thermal Safety", 16, required=False),
        node("17", "Performance Testing", 17, children=[
            node("17.1", "Bench (Non-Clinical) Performance Testing", 1),
            node("17.2", "Animal Performance Testing", 2, required=False),
            node("17.3", "Clinical Performance Testing", 3, required=False),
        ]),
        node("18", "Administrative Documentation", 18, children=[
            node("18.1", "510(k) Summary or Statement", 1),
            node("18.2", "Truthful and Accurate Statement", 2),
            node("18.3", "Declarations of Conformity and Summary Reports", 3),
            node("18.4", "Financial Certification or Disclosure (Forms FDA 3454 / 3455)", 4, required=False),
            node("18.5", "Class III Summary and Certification", 5, required=False),
        ]),
    ],
    # FDA Premarket Approval (PMA) — content aligned to the application contents
    # of 21 CFR 814.20(b). Nonclinical study sub-sections are device-conditional
    # (required=False). SOURCE / VERIFY: 21 CFR 814.20(b) + FDA PMA guidance;
    # reconcile against the current eCFR text before treating as authoritative.
    "FDA_PMA": [
        node("1", "Administrative and Cover Letter", 1, children=[
            node("1.1", "Cover Letter and Table of Contents", 1),
            node("1.2", "Medical Device User Fee Cover Sheet (Form FDA 3601)", 2),
            node("1.3", "CDRH Premarket Review Submission Cover Sheet (Form FDA 3514)", 3),
        ]),
        node("2", "Summary", 2, children=[
            node("2.1", "Indications for Use", 1),
            node("2.2", "Device Description Summary", 2),
            node("2.3", "Alternative Practices and Procedures", 3),
            node("2.4", "Marketing History", 4, required=False),
            node("2.5", "Summary of Safety and Effectiveness Data (SSED)", 5),
        ]),
        node("3", "Device Description and Manufacturing", 3, children=[
            node("3.1", "Complete Device Description", 1),
            node("3.2", "Manufacturing Methods, Facilities and Controls", 2),
            node("3.3", "Reference to Performance Standards", 3, required=False),
        ]),
        node("4", "Nonclinical Laboratory Studies", 4, children=[
            node("4.1", "Biocompatibility", 1, required=False),
            node("4.2", "Sterilization and Shelf Life", 2, required=False),
            node("4.3", "Software / Firmware", 3, required=False),
            node("4.4", "Electrical Safety and Electromagnetic Compatibility", 4, required=False),
            node("4.5", "Bench and Animal Testing", 5, required=False),
        ]),
        node("5", "Clinical Investigations", 5, children=[
            node("5.1", "Study Protocol and Results", 1),
            node("5.2", "Statistical Analysis", 2),
            node("5.3", "Investigator Information and Financial Disclosure", 3),
        ]),
        node("6", "Proposed Labeling", 6),
        node("7", "Quality System Information (Manufacturing)", 7),
        node("8", "Bibliography", 8, required=False),
        node("9", "Environmental Assessment", 9, required=False),
        node("10", "Financial Certification or Disclosure (Forms FDA 3454 / 3455)", 10),
    ],
    # FDA Investigational Device Exemption (IDE) — aligned to 21 CFR 812.20 /
    # 812.25 (investigational plan) / 812.27 (report of prior investigations).
    # SOURCE / VERIFY: 21 CFR Part 812; reconcile against current eCFR text.
    "FDA_IDE": [
        node("1", "Cover Letter and Administrative", 1),
        node("2", "Report of Prior Investigations", 2),
        node("3", "Investigational Plan", 3, children=[
            node("3.1", "Purpose and Protocol", 1),
            node("3.2", "Risk Analysis", 2),
            node("3.3", "Description of Device", 3),
            node("3.4", "Monitoring Procedures", 4),
        ]),
        node("4", "Manufacturing Information", 4),
        node("5", "Investigator Agreements and Certification", 5),
        node("6", "IRB Information and Informed Consent", 6),
        node("7", "Labeling for Investigational Use", 7),
    ],
}

PROFILE_STRUCTURE: dict[str, str] = {
    "510K": "FDA_510K",
    "DE-NOVO": "FDA_510K",
    "PMA": "FDA_PMA",
    "IDE": "FDA_IDE",
}

RELEASE_NOTES: dict[str, str] = {
    "FDA_510K": "2025.2 — realigned to the FDA eSTAR 510(k) section set (18 top-level sections incl. Consensus Standards, Classification, Reprocessing, Sterility, Shelf Life, Cybersecurity). Pending RA verification against the live eSTAR PDF.",
    "FDA_PMA": "2025.2 — aligned to 21 CFR 814.20(b) PMA application contents (Summary/SSED, nonclinical, clinical, labeling, bibliography, environmental assessment, financial disclosure). Pending RA verification.",
    "FDA_IDE": "2025.2 — aligned to 21 CFR Part 812 (investigational plan + report of prior investigations). Pending RA verification.",
}
