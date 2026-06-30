"""Export processors. Selected by the ``package`` business value."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from app.registry.implementations.base import ExportProcessor


class ZipExportProcessor(ExportProcessor):
    """Compressed, folder-structured ZIP package."""

    package_format = "zip"

    def export(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._descriptor(payload)


class ECopyExportProcessor(ExportProcessor):
    """eCopy media — uncompressed by definition."""

    package_format = "ecopy"

    @property
    def compression(self) -> bool:
        return False

    def export(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        descriptor = self._descriptor(payload)
        descriptor["media_type"] = self.configuration.get("mediaType", "electronic")
        return descriptor


class BundleExportProcessor(ExportProcessor):
    """A structured bundle that may carry a Declaration of Conformity."""

    package_format = "bundle"

    def export(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        descriptor = self._descriptor(payload)
        descriptor["bundled"] = True
        descriptor["includes_declaration_of_conformity"] = bool(
            self.configuration.get("includeDeclarationOfConformity", False)
        )
        return descriptor
