"""
Central seed runner.

Discovers ecosystem packages automatically (any sub-package of
``app.regulatory.seed`` exposing an ``ECOSYSTEM``), so adding a new country is a
matter of creating one folder — no change here.

Operations:
    seed_all()                      — every country
    seed_country(code)              — one country
    seed_authority(authority_name)  — re-seed the ecosystem for an authority
    seed_templates(code=None)       — re-seed templates only (one or all)
    seed_configuration_only()       — configuration registry only

All operations are idempotent and safe to run repeatedly.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.regulatory.seed.common import (
    CONFIGURATION_TYPES,
    COMMON_CONFIGURATION_PROFILES,
)
from app.regulatory.seed.framework import (
    Ecosystem,
    EcosystemSeeder,
    SeedContext,
    Stats,
    seed_configuration_profiles,
    seed_configuration_types,
)

logger = logging.getLogger(__name__)


class SeedRunner:
    """Runs the modular ecosystem seeds against a database session."""

    def __init__(self, db: Optional[Session] = None):
        self._db = db
        self._owns_session = db is None
        self._ecosystems: Optional[dict[str, Ecosystem]] = None

    # ------------------------------------------------------------------ #
    # Discovery
    # ------------------------------------------------------------------ #
    def ecosystems(self) -> dict[str, Ecosystem]:
        """Discover and cache all ecosystem packages (by country code)."""
        if self._ecosystems is None:
            import app.regulatory.seed as seed_pkg

            found: dict[str, Ecosystem] = {}
            for modinfo in pkgutil.iter_modules(seed_pkg.__path__, seed_pkg.__name__ + "."):
                if not modinfo.ispkg:
                    continue  # framework/common/runner are modules, not packages
                module = importlib.import_module(modinfo.name)
                eco = getattr(module, "ECOSYSTEM", None)
                if isinstance(eco, Ecosystem):
                    found[eco.code] = eco
            self._ecosystems = found
        return self._ecosystems

    def _ecosystem_by_authority(self, authority_name: str) -> Optional[Ecosystem]:
        for eco in self.ecosystems().values():
            if eco.authority_name.lower() == authority_name.lower():
                return eco
        return None

    # ------------------------------------------------------------------ #
    # Session plumbing
    # ------------------------------------------------------------------ #
    def _run(self, work, *, commit: bool) -> dict[str, int]:
        db = self._db or SessionLocal()
        stats = Stats()
        ctx = SeedContext(db, stats)
        try:
            work(ctx)
            if commit:
                db.commit()
            logger.info("Seed complete: %d created, %d reused", stats.created, stats.reused)
            return {"created": stats.created, "reused": stats.reused}
        except Exception:
            if self._owns_session:
                db.rollback()
            logger.exception("Seed failed, rolled back")
            raise
        finally:
            if self._owns_session:
                db.close()

    def _seed_common(self, ctx: SeedContext) -> None:
        seed_configuration_types(ctx, CONFIGURATION_TYPES)
        seed_configuration_profiles(ctx, COMMON_CONFIGURATION_PROFILES)

    # ------------------------------------------------------------------ #
    # Operations
    # ------------------------------------------------------------------ #
    def seed_all(self, *, commit: bool = True) -> dict[str, int]:
        def work(ctx: SeedContext):
            self._seed_common(ctx)
            for code in sorted(self.ecosystems()):
                EcosystemSeeder(ctx, self.ecosystems()[code]).seed_all()
        return self._run(work, commit=commit)

    def seed_country(self, code: str, *, commit: bool = True) -> dict[str, int]:
        eco = self.ecosystems().get(code.upper())
        if eco is None:
            raise ValueError(f"Unknown country code: {code!r}. Known: {sorted(self.ecosystems())}")

        def work(ctx: SeedContext):
            self._seed_common(ctx)            # config types + shared profiles the country may reference
            EcosystemSeeder(ctx, eco).seed_all()
        return self._run(work, commit=commit)

    def seed_authority(self, authority_name: str, *, commit: bool = True) -> dict[str, int]:
        eco = self._ecosystem_by_authority(authority_name)
        if eco is None:
            authorities = sorted(e.authority_name for e in self.ecosystems().values())
            raise ValueError(f"Unknown authority: {authority_name!r}. Known: {authorities}")

        def work(ctx: SeedContext):
            self._seed_common(ctx)
            EcosystemSeeder(ctx, eco).seed_all()
        return self._run(work, commit=commit)

    def seed_templates(self, code: Optional[str] = None, *, commit: bool = True) -> dict[str, int]:
        if code is not None and code.upper() not in self.ecosystems():
            raise ValueError(f"Unknown country code: {code!r}. Known: {sorted(self.ecosystems())}")
        targets = [self.ecosystems()[code.upper()]] if code else list(self.ecosystems().values())

        def work(ctx: SeedContext):
            for eco in targets:
                EcosystemSeeder(ctx, eco).seed_templates()
        return self._run(work, commit=commit)

    def seed_configuration_only(self, *, commit: bool = True) -> dict[str, int]:
        def work(ctx: SeedContext):
            self._seed_common(ctx)
            for eco in self.ecosystems().values():
                EcosystemSeeder(ctx, eco).seed_configuration()
        return self._run(work, commit=commit)
