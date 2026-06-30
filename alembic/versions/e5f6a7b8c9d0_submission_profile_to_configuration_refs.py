"""refactor submission_profiles: inline config -> configuration_profiles refs

Replaces the inline strategy/language/upload/metadata columns on
``submission_profiles`` with four foreign keys into ``configuration_profiles``:
export, workflow, validation and AI pipeline.

Data migration (no data loss):
- Ensures the four ConfigurationTypes exist (EXPORT, WORKFLOW, VALIDATION,
  AI_PIPELINE) and a DEFAULT ConfigurationProfile for each.
- For every existing submission profile, the inline configuration is bucketed by
  dimension and, where present, captured in a per-profile ConfigurationProfile.
  Dimensions with no data point at the shared DEFAULT profile so every reference
  is populated.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-30 10:00:00.000000

"""
import json
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


MIGRATION_ACTOR = "system-migration"

# Legacy columns being removed, grouped by the configuration dimension that
# absorbs them. Export is the catch-all for packaging/language/upload/metadata.
EXPORT_FIELDS = [
    "submission_method",
    "package_format",
    "export_strategy",
    "default_language",
    "supported_languages",
    "max_upload_size_mb",
    "supported_file_extensions",
]
WORKFLOW_FIELDS = ["workflow_strategy"]
VALIDATION_FIELDS = ["validation_strategy"]
AI_FIELDS = ["ai_prompt_profile"]

CONFIG_TYPES = [
    ("EXPORT", "Export", "Configurations governing how submissions are exported/packaged."),
    ("WORKFLOW", "Workflow", "Configurations governing submission workflow stages and transitions."),
    ("VALIDATION", "Validation", "Configurations governing validation behaviour and thresholds."),
    ("AI_PIPELINE", "AI Pipeline", "Configurations governing AI processing behaviour and limits."),
]


def _as_obj(value):
    """Return a JSON column value as a Python object (lists/dicts), tolerating str."""
    if value is None or isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return value


def _get_or_create_type(conn, now, code, name, description):
    row = conn.execute(
        text("SELECT id FROM configuration_types WHERE code = :code"), {"code": code}
    ).first()
    if row:
        return row[0]
    type_id = uuid.uuid4()
    conn.execute(
        text(
            """
            INSERT INTO configuration_types
                (id, code, name, description, is_active, created_at, updated_at, created_by, updated_by)
            VALUES (:id, :code, :name, :description, true, :now, :now, :actor, :actor)
            """
        ),
        {"id": type_id, "code": code, "name": name, "description": description,
         "now": now, "actor": MIGRATION_ACTOR},
    )
    return type_id


def _create_profile(conn, now, type_id, code, version, name, description, configuration):
    profile_id = uuid.uuid4()
    conn.execute(
        text(
            """
            INSERT INTO configuration_profiles
                (id, configuration_type_id, name, code, description, version,
                 configuration, is_active, created_at, updated_at, created_by, updated_by)
            VALUES (:id, :type_id, :name, :code, :description, :version,
                    CAST(:configuration AS JSONB), true, :now, :now, :actor, :actor)
            """
        ),
        {
            "id": profile_id, "type_id": type_id, "name": name, "code": code,
            "description": description, "version": version,
            "configuration": json.dumps(configuration) if configuration is not None else None,
            "now": now, "actor": MIGRATION_ACTOR,
        },
    )
    return profile_id


def _get_or_create_default_profile(conn, now, type_id, type_code):
    row = conn.execute(
        text(
            "SELECT id FROM configuration_profiles "
            "WHERE configuration_type_id = :tid AND code = 'DEFAULT' AND version = '1.0'"
        ),
        {"tid": type_id},
    ).first()
    if row:
        return row[0]
    return _create_profile(
        conn, now, type_id, "DEFAULT", "1.0",
        f"Default {type_code} Profile",
        f"Default configuration profile for {type_code} (created during migration).",
        {},
    )


def upgrade() -> None:
    # --- 1. Add the four nullable FK columns + indexes + constraints --------- #
    fk_cols = [
        "export_profile_id",
        "workflow_profile_id",
        "validation_profile_id",
        "ai_pipeline_profile_id",
    ]
    for col in fk_cols:
        op.add_column("submission_profiles", sa.Column(col, sa.UUID(), nullable=True))
        op.create_index(
            op.f(f"ix_submission_profiles_{col}"), "submission_profiles", [col], unique=False
        )
        op.create_foreign_key(
            f"fk_submission_profiles_{col}",
            "submission_profiles",
            "configuration_profiles",
            [col],
            ["id"],
            ondelete="SET NULL",
        )

    # --- 2. Data migration --------------------------------------------------- #
    conn = op.get_bind()
    now = datetime.utcnow()

    type_ids = {}
    default_ids = {}
    for code, name, description in CONFIG_TYPES:
        tid = _get_or_create_type(conn, now, code, name, description)
        type_ids[code] = tid
        default_ids[code] = _get_or_create_default_profile(conn, now, tid, code)

    legacy_cols = EXPORT_FIELDS + WORKFLOW_FIELDS + VALIDATION_FIELDS + AI_FIELDS
    select_cols = ", ".join(["id", "name"] + legacy_cols + ['"metadata"'])
    rows = conn.execute(text(f"SELECT {select_cols} FROM submission_profiles")).mappings().all()

    for row in rows:
        sp_id = row["id"]
        sp_name = row["name"]

        def build(fields, include_metadata=False):
            cfg = {}
            for f in fields:
                v = _as_obj(row[f]) if f in ("supported_languages", "supported_file_extensions") else row[f]
                if v is not None:
                    cfg[f] = v
            if include_metadata:
                md = _as_obj(row["metadata"])
                if md:
                    cfg["metadata"] = md
            return cfg

        buckets = {
            "EXPORT": build(EXPORT_FIELDS, include_metadata=True),
            "WORKFLOW": build(WORKFLOW_FIELDS),
            "VALIDATION": build(VALIDATION_FIELDS),
            "AI_PIPELINE": build(AI_FIELDS),
        }

        fk_values = {}
        for code, fk_col in (
            ("EXPORT", "export_profile_id"),
            ("WORKFLOW", "workflow_profile_id"),
            ("VALIDATION", "validation_profile_id"),
            ("AI_PIPELINE", "ai_pipeline_profile_id"),
        ):
            cfg = buckets[code]
            if cfg:
                # Capture this profile's real configuration (no data lost).
                fk_values[fk_col] = _create_profile(
                    conn, now, type_ids[code],
                    code=f"sp-{sp_id}", version="1.0",
                    name=f"{sp_name} – {code.title()}",
                    description=f"Migrated {code} configuration for submission profile '{sp_name}'.",
                    configuration=cfg,
                )
            else:
                # No data for this dimension -> shared default profile.
                fk_values[fk_col] = default_ids[code]

        conn.execute(
            text(
                """
                UPDATE submission_profiles
                SET export_profile_id = :export_profile_id,
                    workflow_profile_id = :workflow_profile_id,
                    validation_profile_id = :validation_profile_id,
                    ai_pipeline_profile_id = :ai_pipeline_profile_id
                WHERE id = :id
                """
            ),
            {**fk_values, "id": sp_id},
        )

    # --- 3. Drop the legacy inline configuration columns --------------------- #
    for col in legacy_cols:
        op.drop_column("submission_profiles", col)
    op.drop_column("submission_profiles", "metadata")


def downgrade() -> None:
    # --- 1. Re-add the legacy columns (nullable) ----------------------------- #
    op.add_column("submission_profiles", sa.Column("submission_method", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("package_format", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("export_strategy", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("workflow_strategy", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("validation_strategy", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("ai_prompt_profile", sa.String(length=100), nullable=True))
    op.add_column("submission_profiles", sa.Column("default_language", sa.String(length=20), nullable=True))
    op.add_column("submission_profiles", sa.Column("supported_languages", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("submission_profiles", sa.Column("max_upload_size_mb", sa.Integer(), nullable=True))
    op.add_column("submission_profiles", sa.Column("supported_file_extensions", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("submission_profiles", sa.Column("metadata", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # --- 2. Best-effort restore of inline values from the linked profiles ---- #
    conn = op.get_bind()
    rows = conn.execute(
        text(
            """
            SELECT sp.id AS id,
                   ep.configuration AS export_cfg,
                   wp.configuration AS workflow_cfg,
                   vp.configuration AS validation_cfg,
                   ap.configuration AS ai_cfg
            FROM submission_profiles sp
            LEFT JOIN configuration_profiles ep ON ep.id = sp.export_profile_id
            LEFT JOIN configuration_profiles wp ON wp.id = sp.workflow_profile_id
            LEFT JOIN configuration_profiles vp ON vp.id = sp.validation_profile_id
            LEFT JOIN configuration_profiles ap ON ap.id = sp.ai_pipeline_profile_id
            """
        )
    ).mappings().all()

    for row in rows:
        export_cfg = _as_obj(row["export_cfg"]) or {}
        workflow_cfg = _as_obj(row["workflow_cfg"]) or {}
        validation_cfg = _as_obj(row["validation_cfg"]) or {}
        ai_cfg = _as_obj(row["ai_cfg"]) or {}
        params = {
            "submission_method": export_cfg.get("submission_method"),
            "package_format": export_cfg.get("package_format"),
            "export_strategy": export_cfg.get("export_strategy"),
            "default_language": export_cfg.get("default_language"),
            "supported_languages": json.dumps(export_cfg["supported_languages"]) if export_cfg.get("supported_languages") is not None else None,
            "max_upload_size_mb": export_cfg.get("max_upload_size_mb"),
            "supported_file_extensions": json.dumps(export_cfg["supported_file_extensions"]) if export_cfg.get("supported_file_extensions") is not None else None,
            "metadata": json.dumps(export_cfg["metadata"]) if export_cfg.get("metadata") is not None else None,
            "workflow_strategy": workflow_cfg.get("workflow_strategy"),
            "validation_strategy": validation_cfg.get("validation_strategy"),
            "ai_prompt_profile": ai_cfg.get("ai_prompt_profile"),
            "id": row["id"],
        }
        conn.execute(
            text(
                """
                UPDATE submission_profiles
                SET submission_method = :submission_method,
                    package_format = :package_format,
                    export_strategy = :export_strategy,
                    default_language = :default_language,
                    supported_languages = CAST(:supported_languages AS JSONB),
                    max_upload_size_mb = :max_upload_size_mb,
                    supported_file_extensions = CAST(:supported_file_extensions AS JSONB),
                    "metadata" = CAST(:metadata AS JSONB),
                    workflow_strategy = :workflow_strategy,
                    validation_strategy = :validation_strategy,
                    ai_prompt_profile = :ai_prompt_profile
                WHERE id = :id
                """
            ),
            params,
        )

    # --- 3. Drop the FK columns --------------------------------------------- #
    for col in (
        "export_profile_id",
        "workflow_profile_id",
        "validation_profile_id",
        "ai_pipeline_profile_id",
    ):
        op.drop_constraint(f"fk_submission_profiles_{col}", "submission_profiles", type_="foreignkey")
        op.drop_index(op.f(f"ix_submission_profiles_{col}"), table_name="submission_profiles")
        op.drop_column("submission_profiles", col)
