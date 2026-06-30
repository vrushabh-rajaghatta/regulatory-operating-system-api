"""
Configuration Registry module.

A reusable registry of business configurations that are referenced by name
elsewhere in the platform (e.g. by a SubmissionProfile's strategy identifiers).

It is built around two global, organization-agnostic entities:

    ConfigurationType 1---* ConfigurationProfile

A ConfigurationType is a category of configuration (EXPORT, WORKFLOW,
VALIDATION, AI_PIPELINE, ...). A ConfigurationProfile is a named, versioned
bundle of BUSINESS configuration stored as JSON.

Important: the ``configuration`` JSON holds business configuration only. It
deliberately does NOT store implementation class names, Python module names or
service names — those are wiring concerns resolved in code, never persisted as
data.
"""
