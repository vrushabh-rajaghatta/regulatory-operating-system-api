"""Validation processors. Selected by the ``processor`` business strategy."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from app.registry.implementations.base import ValidationProcessor


class StandardValidationProcessor(ValidationProcessor):
    """Applies the generic validation flags present in the configuration."""

    def validate(self, target: Mapping[str, Any]) -> Dict[str, Any]:
        cfg = self.configuration
        issues: List[Dict[str, Any]] = []

        if cfg.get("requiredDocuments"):
            issues += [
                {"rule": "requiredDocuments", "severity": "Error",
                 "message": f"Missing required document: {d.get('document_name')}"}
                for d in target.get("required_documents", [])
                if d.get("is_required", True) and d.get("status") != "provided"
            ]

        if cfg.get("enforceMandatorySections"):
            issues += [
                {"rule": "enforceMandatorySections", "severity": "Error",
                 "message": f"Incomplete mandatory section: {s.get('section_code')}"}
                for s in target.get("sections", [])
                if s.get("is_required", True) and not s.get("is_completed", False)
            ]

        threshold = cfg.get("minimumConfidence")
        if threshold is not None:
            for item in target.get("confidences", []):
                if item.get("confidence", 1.0) < float(threshold):
                    issues.append(
                        {"rule": "minimumConfidence", "severity": "Warning",
                         "message": f"{item.get('ref')} confidence below {threshold}"}
                    )

        if cfg.get("requireDeclarationOfConformity") and not target.get(
            "has_declaration_of_conformity", False
        ):
            issues.append(
                {"rule": "requireDeclarationOfConformity", "severity": "Error",
                 "message": "Declaration of Conformity is required"}
            )

        if cfg.get("requireClinicalEvaluation") and not target.get(
            "has_clinical_evaluation", False
        ):
            issues.append(
                {"rule": "requireClinicalEvaluation", "severity": "Error",
                 "message": "Clinical Evaluation is required"}
            )

        return self._report(issues)


class HealthCanadaValidationProcessor(StandardValidationProcessor):
    """
    Extends the standard checks with bilingual enforcement.

    The required languages come from the configuration (e.g. ``["en", "fr"]``),
    so this is selected by business behaviour — not by any authority name.
    """

    def validate(self, target: Mapping[str, Any]) -> Dict[str, Any]:
        report = super().validate(target)
        required = set(self.configuration.get("languages", []))
        present = set(target.get("languages", []))
        missing = sorted(required - present)
        if missing:
            report["issues"].append(
                {"rule": "languages", "severity": "Error",
                 "message": f"Missing required language(s): {', '.join(missing)}"}
            )
            report["passed"] = not any(i["severity"] == "Error" for i in report["issues"])
        return report
