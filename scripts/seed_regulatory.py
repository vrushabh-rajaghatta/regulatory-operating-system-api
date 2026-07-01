#!/usr/bin/env python3
"""Seed the regulatory engine reference hierarchy.

Seeds every regulatory ecosystem (Health Canada, FDA, EU MDR/IVDR, TGA, PMDA):
Country > Authority > Regulation > Submission Type > Submission Profile >
Template Version 2025.1, with template sections, required documents and
validation rules.

Usage:
    python scripts/seed_regulatory.py

Safe to run multiple times: the seed is idempotent (every entity is looked up by
its natural key and only created if absent).
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import app.models  # noqa: F401  Register all models with SQLAlchemy metadata.
from app.regulatory.seed import seed_regulatory_data


if __name__ == "__main__":
    result = seed_regulatory_data()
    print(f"Done. {result['created']} created, {result['reused']} reused.")
