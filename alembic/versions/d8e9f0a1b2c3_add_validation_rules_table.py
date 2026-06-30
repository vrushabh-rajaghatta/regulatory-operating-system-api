"""add validation_rules table (database-driven validation framework)

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2026-06-27 03:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8e9f0a1b2c3'
down_revision = 'c7d8e9f0a1b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'validation_rules',
        sa.Column('template_version_id', sa.UUID(), nullable=False),
        sa.Column('target_type', sa.Enum('DOCUMENT', 'SECTION', 'SUBMISSION', name='validationtargettype'), nullable=False),
        sa.Column('target_reference', sa.String(length=255), nullable=True),
        sa.Column('rule_type', sa.String(length=100), nullable=False),
        sa.Column('rule_expression', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('severity', sa.Enum('ERROR', 'WARNING', 'INFO', name='validationseverity'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['template_version_id'], ['template_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_validation_rules_id'), 'validation_rules', ['id'], unique=False)
    op.create_index(op.f('ix_validation_rules_is_active'), 'validation_rules', ['is_active'], unique=False)
    op.create_index(op.f('ix_validation_rules_rule_type'), 'validation_rules', ['rule_type'], unique=False)
    op.create_index(op.f('ix_validation_rules_severity'), 'validation_rules', ['severity'], unique=False)
    op.create_index(op.f('ix_validation_rules_target_reference'), 'validation_rules', ['target_reference'], unique=False)
    op.create_index(op.f('ix_validation_rules_target_type'), 'validation_rules', ['target_type'], unique=False)
    op.create_index(op.f('ix_validation_rules_template_version_id'), 'validation_rules', ['template_version_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_validation_rules_template_version_id'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_target_type'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_target_reference'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_severity'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_rule_type'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_is_active'), table_name='validation_rules')
    op.drop_index(op.f('ix_validation_rules_id'), table_name='validation_rules')
    op.drop_table('validation_rules')

    # Drop the enum types created for validation_rules.
    sa.Enum(name='validationtargettype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='validationseverity').drop(op.get_bind(), checkfirst=True)
