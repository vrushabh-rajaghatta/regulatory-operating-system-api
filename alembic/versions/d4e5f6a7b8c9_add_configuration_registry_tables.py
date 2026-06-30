"""add configuration registry tables (configuration_types, configuration_profiles)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-30 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- configuration_types --- #
    op.create_table(
        'configuration_types',
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        # Base columns
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_configuration_types_code'), 'configuration_types', ['code'], unique=True)
    op.create_index(op.f('ix_configuration_types_id'), 'configuration_types', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_types_is_active'), 'configuration_types', ['is_active'], unique=False)
    op.create_index(op.f('ix_configuration_types_name'), 'configuration_types', ['name'], unique=False)

    # --- configuration_profiles --- #
    op.create_table(
        'configuration_profiles',
        sa.Column('configuration_type_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        # Base columns
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['configuration_type_id'], ['configuration_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('configuration_type_id', 'code', 'version', name='uq_configuration_profiles_type_code_version'),
    )
    op.create_index(op.f('ix_configuration_profiles_code'), 'configuration_profiles', ['code'], unique=False)
    op.create_index(op.f('ix_configuration_profiles_configuration_type_id'), 'configuration_profiles', ['configuration_type_id'], unique=False)
    op.create_index(op.f('ix_configuration_profiles_id'), 'configuration_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_configuration_profiles_is_active'), 'configuration_profiles', ['is_active'], unique=False)
    op.create_index(op.f('ix_configuration_profiles_name'), 'configuration_profiles', ['name'], unique=False)
    op.create_index(op.f('ix_configuration_profiles_version'), 'configuration_profiles', ['version'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_configuration_profiles_version'), table_name='configuration_profiles')
    op.drop_index(op.f('ix_configuration_profiles_name'), table_name='configuration_profiles')
    op.drop_index(op.f('ix_configuration_profiles_is_active'), table_name='configuration_profiles')
    op.drop_index(op.f('ix_configuration_profiles_id'), table_name='configuration_profiles')
    op.drop_index(op.f('ix_configuration_profiles_configuration_type_id'), table_name='configuration_profiles')
    op.drop_index(op.f('ix_configuration_profiles_code'), table_name='configuration_profiles')
    op.drop_table('configuration_profiles')

    op.drop_index(op.f('ix_configuration_types_name'), table_name='configuration_types')
    op.drop_index(op.f('ix_configuration_types_is_active'), table_name='configuration_types')
    op.drop_index(op.f('ix_configuration_types_id'), table_name='configuration_types')
    op.drop_index(op.f('ix_configuration_types_code'), table_name='configuration_types')
    op.drop_table('configuration_types')
