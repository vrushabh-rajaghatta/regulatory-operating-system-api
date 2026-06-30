"""
Shared seed data used across all ecosystems.

- Configuration types (global: EXPORT / WORKFLOW / VALIDATION / AI_PIPELINE).
- The shared STANDARD_REVIEW workflow profile (reused by several jurisdictions
  for administrative submissions).
- The global industry catalog (Medical Device, IVD), deduped by code.

Pure data — no engine logic.
"""

from __future__ import annotations

from typing import Any

# Industry catalog (global; referenced by code from each country's master data).
INDUSTRIES: dict[str, dict[str, str]] = {
    "MEDDEV": {"name": "Medical Device", "description": "Medical device industry."},
    "IVD": {"name": "In Vitro Diagnostic", "description": "In vitro diagnostic medical device industry."},
}

# The four global configuration types.
CONFIGURATION_TYPES: list[dict[str, str]] = [
    {"code": "EXPORT", "name": "Export", "description": "Configurations governing how submissions are exported/packaged."},
    {"code": "WORKFLOW", "name": "Workflow", "description": "Configurations governing submission workflow stages and transitions."},
    {"code": "VALIDATION", "name": "Validation", "description": "Configurations governing validation behaviour and thresholds."},
    {"code": "AI_PIPELINE", "name": "AI Pipeline", "description": "Configurations governing AI processing behaviour and limits."},
]

# Shared configuration profiles (not specific to any one jurisdiction).
COMMON_CONFIGURATION_PROFILES: dict[str, list[dict[str, Any]]] = {
    "WORKFLOW": [
        {
            "code": "STANDARD_REVIEW",
            "name": "Standard Review",
            "version": "1.0",
            "description": "Baseline review workflow for administrative submissions.",
            "configuration": {
                "states": ["Draft", "Review", "Approved"],
                "requiresDualApproval": False,
            },
        },
    ],
}
