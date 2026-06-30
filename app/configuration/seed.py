"""
Configuration Registry seed (delegator).

The configuration profile data now lives inside the modular regulatory seed
framework — shared types/profiles in ``app.regulatory.seed.common`` and each
jurisdiction's profiles in ``app.regulatory.seed.<country>.configuration``.

This module preserves the historical public entry point ``seed_configuration_data``
(used at application startup behind ``SEED_CONFIGURATION``) by delegating to the
framework's configuration-only seeding. It remains idempotent.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session


def seed_configuration_data(db: Optional[Session] = None, *, commit: bool = True) -> dict[str, int]:
    """Seed the Configuration Registry (types + all jurisdictions' profiles), idempotently."""
    from app.regulatory.seed.runner import SeedRunner

    return SeedRunner(db).seed_configuration_only(commit=commit)
