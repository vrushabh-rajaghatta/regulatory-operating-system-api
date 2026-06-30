"""add submissions.submission_profile_id (nullable, additive)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-27 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('submissions', sa.Column('submission_profile_id', sa.UUID(), nullable=True))
    op.create_index(
        op.f('ix_submissions_submission_profile_id'),
        'submissions', ['submission_profile_id'], unique=False,
    )
    op.create_foreign_key(
        'fk_submissions_submission_profile_id_submission_profiles',
        'submissions', 'submission_profiles',
        ['submission_profile_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_submissions_submission_profile_id_submission_profiles',
        'submissions', type_='foreignkey',
    )
    op.drop_index(op.f('ix_submissions_submission_profile_id'), table_name='submissions')
    op.drop_column('submissions', 'submission_profile_id')
