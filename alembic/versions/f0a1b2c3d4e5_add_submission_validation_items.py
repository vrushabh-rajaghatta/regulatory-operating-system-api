"""add submission_validation_items table (per-submission validation checklist)

Revision ID: f0a1b2c3d4e5
Revises: e9f0a1b2c3d4
Create Date: 2026-06-27 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0a1b2c3d4e5'
down_revision = 'e9f0a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'submission_validation_items',
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('validation_rule_id', sa.UUID(), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_reference', sa.String(length=255), nullable=True),
        sa.Column('rule_type', sa.String(length=100), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validation_rule_id'], ['validation_rules.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_submission_validation_items_id'), 'submission_validation_items', ['id'], unique=False)
    op.create_index(op.f('ix_submission_validation_items_status'), 'submission_validation_items', ['status'], unique=False)
    op.create_index(op.f('ix_submission_validation_items_submission_id'), 'submission_validation_items', ['submission_id'], unique=False)
    op.create_index(op.f('ix_submission_validation_items_validation_rule_id'), 'submission_validation_items', ['validation_rule_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submission_validation_items_validation_rule_id'), table_name='submission_validation_items')
    op.drop_index(op.f('ix_submission_validation_items_submission_id'), table_name='submission_validation_items')
    op.drop_index(op.f('ix_submission_validation_items_status'), table_name='submission_validation_items')
    op.drop_index(op.f('ix_submission_validation_items_id'), table_name='submission_validation_items')
    op.drop_table('submission_validation_items')
