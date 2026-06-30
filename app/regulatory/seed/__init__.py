"""
Modular regulatory seed framework.

Seed data is organised by ecosystem (one package per country); the engine lives
in ``framework.py`` and discovery/orchestration in ``runner.py``. Adding a new
country means adding one folder with the six data modules and an ``ECOSYSTEM``
export — no existing code changes.

Public API (backward-compatible):
    seed_regulatory_data(db=None, commit=True)   — seed everything (all countries)
    SeedRunner                                   — selective seeding
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.regulatory.seed.framework import (
    Ecosystem,
    EcosystemSeeder,
    SeedContext,
    Stats,
    doc,
    doc_rule,
    node,
    section_rule,
)
from app.regulatory.seed.runner import SeedRunner


def seed_regulatory_data(db: Optional[Session] = None, *, commit: bool = True) -> dict[str, int]:
    """Seed all regulatory ecosystems idempotently. Returns {'created': n, 'reused': n}."""
    return SeedRunner(db).seed_all(commit=commit)


__all__ = [
    "SeedRunner",
    "seed_regulatory_data",
    "Ecosystem",
    "EcosystemSeeder",
    "SeedContext",
    "Stats",
    "node",
    "doc",
    "doc_rule",
    "section_rule",
]
