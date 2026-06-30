"""add section_rules table (template section <-> required document links)

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2026-06-27 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9f0a1b2c3d4'
down_revision = 'd8e9f0a1b2c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'section_rules',
        sa.Column('template_section_id', sa.UUID(), nullable=False),
        sa.Column('required_document_id', sa.UUID(), nullable=False),
        sa.Column('rule_type', sa.String(length=100), nullable=False),
        sa.Column('confidence_threshold', sa.Float(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['template_section_id'], ['template_sections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['required_document_id'], ['required_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'template_section_id', 'required_document_id', 'rule_type',
            name='uq_section_rules_section_document_rule_type',
        ),
    )
    op.create_index(op.f('ix_section_rules_id'), 'section_rules', ['id'], unique=False)
    op.create_index(op.f('ix_section_rules_required_document_id'), 'section_rules', ['required_document_id'], unique=False)
    op.create_index(op.f('ix_section_rules_rule_type'), 'section_rules', ['rule_type'], unique=False)
    op.create_index(op.f('ix_section_rules_template_section_id'), 'section_rules', ['template_section_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_section_rules_template_section_id'), table_name='section_rules')
    op.drop_index(op.f('ix_section_rules_rule_type'), table_name='section_rules')
    op.drop_index(op.f('ix_section_rules_required_document_id'), table_name='section_rules')
    op.drop_index(op.f('ix_section_rules_id'), table_name='section_rules')
    op.drop_table('section_rules')
