"""add submission_types table to the regulatory engine

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-27 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'submission_types',
        sa.Column('regulation_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_prefix', sa.String(length=50), nullable=True),
        sa.Column('allows_multiple_sequences', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('regulation_id', 'code', name='uq_submission_types_regulation_id_code'),
    )
    op.create_index(op.f('ix_submission_types_code'), 'submission_types', ['code'], unique=False)
    op.create_index(op.f('ix_submission_types_id'), 'submission_types', ['id'], unique=False)
    op.create_index(op.f('ix_submission_types_is_active'), 'submission_types', ['is_active'], unique=False)
    op.create_index(op.f('ix_submission_types_name'), 'submission_types', ['name'], unique=False)
    op.create_index(op.f('ix_submission_types_regulation_id'), 'submission_types', ['regulation_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submission_types_regulation_id'), table_name='submission_types')
    op.drop_index(op.f('ix_submission_types_name'), table_name='submission_types')
    op.drop_index(op.f('ix_submission_types_is_active'), table_name='submission_types')
    op.drop_index(op.f('ix_submission_types_id'), table_name='submission_types')
    op.drop_index(op.f('ix_submission_types_code'), table_name='submission_types')
    op.drop_table('submission_types')
