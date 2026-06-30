"""add template_versions table (versioned templates per submission type / risk class)

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-06-27 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'template_versions',
        sa.Column('submission_type_id', sa.UUID(), nullable=False),
        sa.Column('risk_classification_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'DEPRECATED', name='templatestatus'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_latest', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['submission_type_id'], ['submission_types.id'], ),
        sa.ForeignKeyConstraint(['risk_classification_id'], ['risk_classifications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'submission_type_id', 'risk_classification_id', 'version',
            name='uq_template_versions_type_risk_version',
        ),
    )
    op.create_index(op.f('ix_template_versions_id'), 'template_versions', ['id'], unique=False)
    op.create_index(op.f('ix_template_versions_is_latest'), 'template_versions', ['is_latest'], unique=False)
    op.create_index(op.f('ix_template_versions_risk_classification_id'), 'template_versions', ['risk_classification_id'], unique=False)
    op.create_index(op.f('ix_template_versions_status'), 'template_versions', ['status'], unique=False)
    op.create_index(op.f('ix_template_versions_submission_type_id'), 'template_versions', ['submission_type_id'], unique=False)
    op.create_index(op.f('ix_template_versions_version'), 'template_versions', ['version'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_template_versions_version'), table_name='template_versions')
    op.drop_index(op.f('ix_template_versions_submission_type_id'), table_name='template_versions')
    op.drop_index(op.f('ix_template_versions_status'), table_name='template_versions')
    op.drop_index(op.f('ix_template_versions_risk_classification_id'), table_name='template_versions')
    op.drop_index(op.f('ix_template_versions_is_latest'), table_name='template_versions')
    op.drop_index(op.f('ix_template_versions_id'), table_name='template_versions')
    op.drop_table('template_versions')

    # Drop the enum type created for template_versions.status
    sa.Enum(name='templatestatus').drop(op.get_bind(), checkfirst=True)
