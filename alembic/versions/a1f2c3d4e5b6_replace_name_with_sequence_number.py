"""replace submissions.name with sequence_number

Revision ID: a1f2c3d4e5b6
Revises: ce76cc308471
Create Date: 2026-06-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1f2c3d4e5b6'
down_revision = 'ce76cc308471'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add sequence_number column (nullable for backfill).
    op.add_column(
        'submissions',
        sa.Column('sequence_number', sa.String(length=32), nullable=True),
    )
    op.create_index(
        op.f('ix_submissions_sequence_number'),
        'submissions',
        ['sequence_number'],
        unique=False,
    )

    # 2. Backfill: zero-padded sequential numbers per product, ordered by created_at.
    conn = op.get_bind()
    conn.execute(sa.text(
        """
        WITH numbered AS (
            SELECT
                id,
                LPAD(
                    (ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY created_at, id) - 1)::text,
                    4,
                    '0'
                ) AS new_number
            FROM submissions
        )
        UPDATE submissions s
        SET sequence_number = numbered.new_number
        FROM numbered
        WHERE s.id = numbered.id;
        """
    ))

    # 3. Enforce NOT NULL + per-product uniqueness now that values are populated.
    op.alter_column(
        'submissions',
        'sequence_number',
        existing_type=sa.String(length=32),
        nullable=False,
    )
    op.create_unique_constraint(
        'uq_submissions_product_id_sequence_number',
        'submissions',
        ['product_id', 'sequence_number'],
    )

    # 4. Drop the old name column and its index.
    op.drop_index(op.f('ix_submissions_name'), table_name='submissions')
    op.drop_column('submissions', 'name')


def downgrade() -> None:
    op.add_column(
        'submissions',
        sa.Column('name', sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f('ix_submissions_name'),
        'submissions',
        ['name'],
        unique=False,
    )
    op.drop_constraint(
        'uq_submissions_product_id_sequence_number',
        'submissions',
        type_='unique',
    )
    op.drop_index(op.f('ix_submissions_sequence_number'), table_name='submissions')
    op.drop_column('submissions', 'sequence_number')
