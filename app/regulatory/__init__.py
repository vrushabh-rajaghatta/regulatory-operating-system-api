"""
Regulatory Engine module for managing regulatory master data.

This module handles the global reference entities that the regulatory
platform is built on:
- Countries (ISO-coded jurisdictions)
- Authorities (regulatory bodies within a country)
- Industries (Pharmaceutical, Medical Device, etc.)
- Regulations (rules issued by an authority for an industry)

These are shared master entities (not organization-scoped) consumed across
projects, products and submissions.
"""
