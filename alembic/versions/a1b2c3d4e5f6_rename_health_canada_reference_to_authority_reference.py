"""rename submissions.health_canada_reference to authority_reference

Generalizes the Health Canada POC field into a jurisdiction-agnostic
authority reference now that the platform supports multiple regulatory
ecosystems (Health Canada, FDA, EU MDR/IVDR, TGA, PMDA).

Revision ID: a1b2c3d4e5f6
Revises: 335660d7aeff
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '335660d7aeff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f('ix_submissions_health_canada_reference'), table_name='submissions')
    op.alter_column(
        'submissions',
        'health_canada_reference',
        new_column_name='authority_reference',
    )
    op.create_index(
        op.f('ix_submissions_authority_reference'),
        'submissions',
        ['authority_reference'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_submissions_authority_reference'), table_name='submissions')
    op.alter_column(
        'submissions',
        'authority_reference',
        new_column_name='health_canada_reference',
    )
    op.create_index(
        op.f('ix_submissions_health_canada_reference'),
        'submissions',
        ['health_canada_reference'],
        unique=False,
    )
