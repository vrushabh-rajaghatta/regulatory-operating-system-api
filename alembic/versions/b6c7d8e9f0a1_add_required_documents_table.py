"""add required_documents table (per template version)

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-06-27 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b6c7d8e9f0a1'
down_revision = 'a5b6c7d8e9f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'required_documents',
        sa.Column('template_version_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required', sa.Boolean(), nullable=False),
        sa.Column('allowed_extensions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('accepted_mime_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('minimum_files', sa.Integer(), nullable=False),
        sa.Column('maximum_files', sa.Integer(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['template_version_id'], ['template_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_version_id', 'name', name='uq_required_documents_version_name'),
    )
    op.create_index(op.f('ix_required_documents_id'), 'required_documents', ['id'], unique=False)
    op.create_index(op.f('ix_required_documents_name'), 'required_documents', ['name'], unique=False)
    op.create_index(op.f('ix_required_documents_required'), 'required_documents', ['required'], unique=False)
    op.create_index(op.f('ix_required_documents_template_version_id'), 'required_documents', ['template_version_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_required_documents_template_version_id'), table_name='required_documents')
    op.drop_index(op.f('ix_required_documents_required'), table_name='required_documents')
    op.drop_index(op.f('ix_required_documents_name'), table_name='required_documents')
    op.drop_index(op.f('ix_required_documents_id'), table_name='required_documents')
    op.drop_table('required_documents')
