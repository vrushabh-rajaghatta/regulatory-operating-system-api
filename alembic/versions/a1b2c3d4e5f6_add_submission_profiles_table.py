"""add submission_profiles table (configuration per submission type)

Revision ID: a1b2c3d4e5f6
Revises: f0a1b2c3d4e5
Create Date: 2026-06-27 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f0a1b2c3d4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'submission_profiles',
        sa.Column('submission_type_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # Submission configuration
        sa.Column('submission_method', sa.String(length=100), nullable=True),
        sa.Column('package_format', sa.String(length=100), nullable=True),
        sa.Column('export_strategy', sa.String(length=100), nullable=True),
        sa.Column('workflow_strategy', sa.String(length=100), nullable=True),
        sa.Column('validation_strategy', sa.String(length=100), nullable=True),
        sa.Column('ai_prompt_profile', sa.String(length=100), nullable=True),
        # Language configuration
        sa.Column('default_language', sa.String(length=20), nullable=True),
        sa.Column('supported_languages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Upload configuration
        sa.Column('max_upload_size_mb', sa.Integer(), nullable=True),
        sa.Column('supported_file_extensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        # Metadata (column literally named "metadata"; ORM attribute is profile_metadata)
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        # Base columns
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['submission_type_id'], ['submission_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_type_id', 'code', name='uq_submission_profiles_type_code'),
    )
    op.create_index(op.f('ix_submission_profiles_code'), 'submission_profiles', ['code'], unique=False)
    op.create_index(op.f('ix_submission_profiles_id'), 'submission_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_submission_profiles_is_active'), 'submission_profiles', ['is_active'], unique=False)
    op.create_index(op.f('ix_submission_profiles_name'), 'submission_profiles', ['name'], unique=False)
    op.create_index(op.f('ix_submission_profiles_submission_type_id'), 'submission_profiles', ['submission_type_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submission_profiles_submission_type_id'), table_name='submission_profiles')
    op.drop_index(op.f('ix_submission_profiles_name'), table_name='submission_profiles')
    op.drop_index(op.f('ix_submission_profiles_is_active'), table_name='submission_profiles')
    op.drop_index(op.f('ix_submission_profiles_id'), table_name='submission_profiles')
    op.drop_index(op.f('ix_submission_profiles_code'), table_name='submission_profiles')
    op.drop_table('submission_profiles')
