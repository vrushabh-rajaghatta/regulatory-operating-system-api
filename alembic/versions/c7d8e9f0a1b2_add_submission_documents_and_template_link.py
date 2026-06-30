"""add submission_documents table and submissions.template_version_id link

Revision ID: c7d8e9f0a1b2
Revises: b6c7d8e9f0a1
Create Date: 2026-06-27 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7d8e9f0a1b2'
down_revision = 'b6c7d8e9f0a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- submissions.template_version_id (nullable, additive) ------------ #
    op.add_column(
        'submissions',
        sa.Column('template_version_id', sa.UUID(), nullable=True),
    )
    op.create_index(
        op.f('ix_submissions_template_version_id'),
        'submissions',
        ['template_version_id'],
        unique=False,
    )
    op.create_foreign_key(
        'fk_submissions_template_version_id_template_versions',
        'submissions',
        'template_versions',
        ['template_version_id'],
        ['id'],
    )

    # --- submission_documents (per-submission required-doc placeholders) -- #
    op.create_table(
        'submission_documents',
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('required_document_id', sa.UUID(), nullable=True),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['required_document_id'], ['required_documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_submission_documents_id'), 'submission_documents', ['id'], unique=False)
    op.create_index(op.f('ix_submission_documents_required_document_id'), 'submission_documents', ['required_document_id'], unique=False)
    op.create_index(op.f('ix_submission_documents_status'), 'submission_documents', ['status'], unique=False)
    op.create_index(op.f('ix_submission_documents_submission_id'), 'submission_documents', ['submission_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submission_documents_submission_id'), table_name='submission_documents')
    op.drop_index(op.f('ix_submission_documents_status'), table_name='submission_documents')
    op.drop_index(op.f('ix_submission_documents_required_document_id'), table_name='submission_documents')
    op.drop_index(op.f('ix_submission_documents_id'), table_name='submission_documents')
    op.drop_table('submission_documents')

    op.drop_constraint(
        'fk_submissions_template_version_id_template_versions',
        'submissions',
        type_='foreignkey',
    )
    op.drop_index(op.f('ix_submissions_template_version_id'), table_name='submissions')
    op.drop_column('submissions', 'template_version_id')
