"""add risk_classifications and submission_type_risk_class mapping

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-06-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- risk_classifications -------------------------------------------- #
    op.create_table(
        'risk_classifications',
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_risk_classifications_code'), 'risk_classifications', ['code'], unique=True)
    op.create_index(op.f('ix_risk_classifications_id'), 'risk_classifications', ['id'], unique=False)
    op.create_index(op.f('ix_risk_classifications_name'), 'risk_classifications', ['name'], unique=False)
    op.create_index(op.f('ix_risk_classifications_sort_order'), 'risk_classifications', ['sort_order'], unique=False)

    # --- submission_type_risk_class (association) ------------------------ #
    op.create_table(
        'submission_type_risk_class',
        sa.Column('submission_type_id', sa.UUID(), nullable=False),
        sa.Column('risk_classification_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['submission_type_id'], ['submission_types.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['risk_classification_id'], ['risk_classifications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('submission_type_id', 'risk_classification_id'),
    )


def downgrade() -> None:
    op.drop_table('submission_type_risk_class')

    op.drop_index(op.f('ix_risk_classifications_sort_order'), table_name='risk_classifications')
    op.drop_index(op.f('ix_risk_classifications_name'), table_name='risk_classifications')
    op.drop_index(op.f('ix_risk_classifications_id'), table_name='risk_classifications')
    op.drop_index(op.f('ix_risk_classifications_code'), table_name='risk_classifications')
    op.drop_table('risk_classifications')
