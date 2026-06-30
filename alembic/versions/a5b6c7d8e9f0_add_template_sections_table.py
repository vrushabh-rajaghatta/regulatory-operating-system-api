"""add template_sections table (hierarchical sections per template version)

Revision ID: a5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-06-27 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5b6c7d8e9f0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'template_sections',
        sa.Column('template_version_id', sa.UUID(), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('section_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('help_text', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['template_version_id'], ['template_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['template_sections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'template_version_id', 'section_number',
            name='uq_template_sections_version_section_number',
        ),
    )
    op.create_index(op.f('ix_template_sections_id'), 'template_sections', ['id'], unique=False)
    op.create_index(op.f('ix_template_sections_is_required'), 'template_sections', ['is_required'], unique=False)
    op.create_index(op.f('ix_template_sections_parent_id'), 'template_sections', ['parent_id'], unique=False)
    op.create_index(op.f('ix_template_sections_section_number'), 'template_sections', ['section_number'], unique=False)
    op.create_index(op.f('ix_template_sections_template_version_id'), 'template_sections', ['template_version_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_template_sections_template_version_id'), table_name='template_sections')
    op.drop_index(op.f('ix_template_sections_section_number'), table_name='template_sections')
    op.drop_index(op.f('ix_template_sections_parent_id'), table_name='template_sections')
    op.drop_index(op.f('ix_template_sections_is_required'), table_name='template_sections')
    op.drop_index(op.f('ix_template_sections_id'), table_name='template_sections')
    op.drop_table('template_sections')
