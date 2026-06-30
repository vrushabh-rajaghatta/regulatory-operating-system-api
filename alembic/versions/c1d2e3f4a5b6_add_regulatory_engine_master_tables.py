"""add regulatory engine master tables (countries, authorities, industries, regulations)

Revision ID: c1d2e3f4a5b6
Revises: b7c8d9e0f1a2
Create Date: 2026-06-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'b7c8d9e0f1a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- countries ------------------------------------------------------- #
    op.create_table(
        'countries',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_countries_code'), 'countries', ['code'], unique=True)
    op.create_index(op.f('ix_countries_id'), 'countries', ['id'], unique=False)
    op.create_index(op.f('ix_countries_is_active'), 'countries', ['is_active'], unique=False)
    op.create_index(op.f('ix_countries_name'), 'countries', ['name'], unique=False)

    # --- industries ------------------------------------------------------ #
    op.create_table(
        'industries',
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_industries_code'), 'industries', ['code'], unique=True)
    op.create_index(op.f('ix_industries_id'), 'industries', ['id'], unique=False)
    op.create_index(op.f('ix_industries_is_active'), 'industries', ['is_active'], unique=False)
    op.create_index(op.f('ix_industries_name'), 'industries', ['name'], unique=False)

    # --- authorities ----------------------------------------------------- #
    op.create_table(
        'authorities',
        sa.Column('country_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('abbreviation', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_id', 'name', name='uq_authorities_country_id_name'),
    )
    op.create_index(op.f('ix_authorities_abbreviation'), 'authorities', ['abbreviation'], unique=False)
    op.create_index(op.f('ix_authorities_country_id'), 'authorities', ['country_id'], unique=False)
    op.create_index(op.f('ix_authorities_id'), 'authorities', ['id'], unique=False)
    op.create_index(op.f('ix_authorities_is_active'), 'authorities', ['is_active'], unique=False)
    op.create_index(op.f('ix_authorities_name'), 'authorities', ['name'], unique=False)

    # --- regulations ----------------------------------------------------- #
    op.create_table(
        'regulations',
        sa.Column('authority_id', sa.UUID(), nullable=False),
        sa.Column('industry_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'DEPRECATED', name='regulationstatus'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['authority_id'], ['authorities.id'], ),
        sa.ForeignKeyConstraint(['industry_id'], ['industries.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('authority_id', 'code', 'version', name='uq_regulations_authority_code_version'),
    )
    op.create_index(op.f('ix_regulations_authority_id'), 'regulations', ['authority_id'], unique=False)
    op.create_index(op.f('ix_regulations_code'), 'regulations', ['code'], unique=False)
    op.create_index(op.f('ix_regulations_id'), 'regulations', ['id'], unique=False)
    op.create_index(op.f('ix_regulations_industry_id'), 'regulations', ['industry_id'], unique=False)
    op.create_index(op.f('ix_regulations_name'), 'regulations', ['name'], unique=False)
    op.create_index(op.f('ix_regulations_status'), 'regulations', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_regulations_status'), table_name='regulations')
    op.drop_index(op.f('ix_regulations_name'), table_name='regulations')
    op.drop_index(op.f('ix_regulations_industry_id'), table_name='regulations')
    op.drop_index(op.f('ix_regulations_id'), table_name='regulations')
    op.drop_index(op.f('ix_regulations_code'), table_name='regulations')
    op.drop_index(op.f('ix_regulations_authority_id'), table_name='regulations')
    op.drop_table('regulations')

    op.drop_index(op.f('ix_authorities_name'), table_name='authorities')
    op.drop_index(op.f('ix_authorities_is_active'), table_name='authorities')
    op.drop_index(op.f('ix_authorities_id'), table_name='authorities')
    op.drop_index(op.f('ix_authorities_country_id'), table_name='authorities')
    op.drop_index(op.f('ix_authorities_abbreviation'), table_name='authorities')
    op.drop_table('authorities')

    op.drop_index(op.f('ix_industries_name'), table_name='industries')
    op.drop_index(op.f('ix_industries_is_active'), table_name='industries')
    op.drop_index(op.f('ix_industries_id'), table_name='industries')
    op.drop_index(op.f('ix_industries_code'), table_name='industries')
    op.drop_table('industries')

    op.drop_index(op.f('ix_countries_name'), table_name='countries')
    op.drop_index(op.f('ix_countries_is_active'), table_name='countries')
    op.drop_index(op.f('ix_countries_id'), table_name='countries')
    op.drop_index(op.f('ix_countries_code'), table_name='countries')
    op.drop_table('countries')

    # Drop the enum type created for regulations.status
    sa.Enum(name='regulationstatus').drop(op.get_bind(), checkfirst=True)
