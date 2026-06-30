"""point template_versions at submission_profiles (with data migration)

Moves TemplateVersion from referencing (submission_type, risk_classification)
directly to referencing SubmissionProfile. Existing template versions are moved
to an automatically-created default SubmissionProfile (one per distinct
submission_type + risk_classification pair, preserving version uniqueness).
No existing data is deleted; `description` is preserved into `release_notes`.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-27 06:00:00.000000

"""
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. New columns, nullable for backfill.
    op.add_column('template_versions', sa.Column('submission_profile_id', sa.UUID(), nullable=True))
    op.add_column('template_versions', sa.Column('expiry_date', sa.Date(), nullable=True))
    op.add_column('template_versions', sa.Column('release_notes', sa.Text(), nullable=True))

    # 2. Data migration: create a default SubmissionProfile per distinct
    #    (submission_type, risk_classification) present in template_versions, and
    #    point those template versions at it. One profile per pair preserves the
    #    new (submission_profile_id, version) uniqueness.
    pairs = bind.execute(sa.text(
        """
        SELECT DISTINCT tv.submission_type_id AS st_id,
                        tv.risk_classification_id AS rc_id,
                        rc.code AS risk_code,
                        rc.name AS risk_name
        FROM template_versions tv
        JOIN risk_classifications rc ON rc.id = tv.risk_classification_id
        """
    )).fetchall()

    now = datetime.utcnow()
    for pair in pairs:
        code = f"DEFAULT-{pair.risk_code}"
        name = f"Default Profile ({pair.risk_name})"

        existing = bind.execute(sa.text(
            "SELECT id FROM submission_profiles WHERE submission_type_id = :st AND code = :code"
        ), {"st": pair.st_id, "code": code}).fetchone()

        if existing:
            profile_id = existing.id
        else:
            profile_id = uuid.uuid4()
            bind.execute(sa.text(
                """
                INSERT INTO submission_profiles
                    (id, submission_type_id, name, code, description, is_active,
                     created_at, updated_at, created_by, updated_by)
                VALUES
                    (:id, :st, :name, :code, :description, true,
                     :now, :now, 'migration', 'migration')
                """
            ), {
                "id": profile_id,
                "st": pair.st_id,
                "name": name,
                "code": code,
                "description": "Auto-created during the TemplateVersion -> SubmissionProfile migration.",
                "now": now,
            })

        bind.execute(sa.text(
            """
            UPDATE template_versions
            SET submission_profile_id = :pid
            WHERE submission_type_id = :st AND risk_classification_id = :rc
            """
        ), {"pid": profile_id, "st": pair.st_id, "rc": pair.rc_id})

    # Preserve the old free-text description into release_notes.
    bind.execute(sa.text(
        "UPDATE template_versions SET release_notes = description "
        "WHERE description IS NOT NULL AND release_notes IS NULL"
    ))

    # 3. Enforce NOT NULL, add index + FK for the new column.
    op.alter_column('template_versions', 'submission_profile_id', existing_type=sa.UUID(), nullable=False)
    op.create_index(
        op.f('ix_template_versions_submission_profile_id'),
        'template_versions', ['submission_profile_id'], unique=False,
    )
    op.create_foreign_key(
        'fk_template_versions_submission_profile_id_submission_profiles',
        'template_versions', 'submission_profiles',
        ['submission_profile_id'], ['id'], ondelete='CASCADE',
    )

    # 4. Drop the old constraint / indexes / FKs / columns.
    op.drop_constraint('uq_template_versions_type_risk_version', 'template_versions', type_='unique')
    op.drop_index('ix_template_versions_submission_type_id', table_name='template_versions')
    op.drop_index('ix_template_versions_risk_classification_id', table_name='template_versions')
    op.drop_constraint('template_versions_submission_type_id_fkey', 'template_versions', type_='foreignkey')
    op.drop_constraint('template_versions_risk_classification_id_fkey', 'template_versions', type_='foreignkey')
    op.drop_column('template_versions', 'submission_type_id')
    op.drop_column('template_versions', 'risk_classification_id')
    op.drop_column('template_versions', 'description')

    # 5. New uniqueness: (submission_profile_id, version).
    op.create_unique_constraint(
        'uq_template_versions_profile_version', 'template_versions',
        ['submission_profile_id', 'version'],
    )


def downgrade() -> None:
    """
    Reverse the structural change. NOTE: lossy — risk_classification_id cannot be
    recovered (the profile only carries submission_type_id), so it is left NULL.
    """
    bind = op.get_bind()

    op.add_column('template_versions', sa.Column('submission_type_id', sa.UUID(), nullable=True))
    op.add_column('template_versions', sa.Column('risk_classification_id', sa.UUID(), nullable=True))
    op.add_column('template_versions', sa.Column('description', sa.Text(), nullable=True))

    # Recover what we can: submission_type_id from the profile, description from release_notes.
    bind.execute(sa.text(
        """
        UPDATE template_versions tv
        SET submission_type_id = sp.submission_type_id
        FROM submission_profiles sp
        WHERE tv.submission_profile_id = sp.id
        """
    ))
    bind.execute(sa.text(
        "UPDATE template_versions SET description = release_notes WHERE description IS NULL"
    ))

    op.drop_constraint('uq_template_versions_profile_version', 'template_versions', type_='unique')
    op.drop_constraint(
        'fk_template_versions_submission_profile_id_submission_profiles',
        'template_versions', type_='foreignkey',
    )
    op.drop_index(op.f('ix_template_versions_submission_profile_id'), table_name='template_versions')
    op.drop_column('template_versions', 'submission_profile_id')
    op.drop_column('template_versions', 'expiry_date')
    op.drop_column('template_versions', 'release_notes')

    op.create_index('ix_template_versions_submission_type_id', 'template_versions', ['submission_type_id'], unique=False)
    op.create_index('ix_template_versions_risk_classification_id', 'template_versions', ['risk_classification_id'], unique=False)
    op.create_foreign_key('template_versions_submission_type_id_fkey', 'template_versions', 'submission_types', ['submission_type_id'], ['id'])
    op.create_foreign_key('template_versions_risk_classification_id_fkey', 'template_versions', 'risk_classifications', ['risk_classification_id'], ['id'])
    op.create_unique_constraint(
        'uq_template_versions_type_risk_version', 'template_versions',
        ['submission_type_id', 'risk_classification_id', 'version'],
    )
