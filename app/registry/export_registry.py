"""ExportRegistry — selects an ExportProcessor from the ``package`` business key."""

from __future__ import annotations

from typing import Any

from app.registry.base import (
    ConfigurationKeyError,
    Registry,
    extract_configuration,
)
from app.registry.implementations.base import ExportProcessor
from app.registry.implementations.export import (
    BundleExportProcessor,
    ECopyExportProcessor,
    ZipExportProcessor,
)


class ExportRegistry(Registry[ExportProcessor]):
    """Maps the ``package`` configuration value to an ExportProcessor."""

    DISCRIMINATOR = "package"

    def resolve(self, profile: Any, **context: Any) -> ExportProcessor:
        cfg = extract_configuration(profile)
        key = cfg.get(self.DISCRIMINATOR)
        if not key:
            raise ConfigurationKeyError(
                f"{self.name}: export configuration missing '{self.DISCRIMINATOR}'"
            )
        return self.create(str(key).lower(), configuration=cfg, **context)


export_registry = ExportRegistry("ExportRegistry")
export_registry.register("zip", ZipExportProcessor)
export_registry.register("ecopy", ECopyExportProcessor)
export_registry.register("bundle", BundleExportProcessor)
