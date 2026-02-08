"""phase1 market data canonical persistence

Revision ID: 0005_market_data_phase1
Revises: 0004_phase1_schema_versioning
Create Date: 2026-02-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_market_data_phase1'
down_revision = '0004_phase1_schema_versioning'
branch_labels = None
depends_on = None


def _enable_rls(table_name: str) -> None:
    op.execute(f'ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;')
    op.execute(f'ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;')
    op.execute(
        f"""
        CREATE POLICY {table_name}_tenant_isolation ON {table_name}
        USING (org_id::text = current_setting('app.current_org_id', true))
        WITH CHECK (org_id::text = current_setting('app.current_org_id', true));
        """
    )


def upgrade() -> None:
    op.add_column(
        'market_timeseries',
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='unknown'),
    )
    op.add_column(
        'market_timeseries',
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='v1'),
    )
    op.add_column(
        'market_timeseries',
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        'market_timeseries',
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute('ALTER TABLE market_timeseries ALTER COLUMN provider DROP DEFAULT;')
    op.execute('ALTER TABLE market_timeseries ALTER COLUMN schema_version DROP DEFAULT;')
    op.create_index(
        'ix_market_timeseries_org_symbol_timeframe_ts',
        'market_timeseries',
        ['org_id', 'symbol', 'timeframe', 'ts'],
    )
    op.create_index('ix_market_timeseries_raw_payload_id', 'market_timeseries', ['raw_payload_id'])
    op.create_index(
        'uq_market_timeseries_org_provider_symbol_timeframe_ts',
        'market_timeseries',
        ['org_id', 'provider', 'symbol', 'timeframe', 'ts'],
        unique=True,
    )

    op.create_table(
        'market_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('schema_version', sa.String(length=32), nullable=False),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('change_percent', sa.Float(), nullable=True),
        sa.Column('as_of', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_market_quotes_org_id', 'market_quotes', ['org_id'])
    op.create_index('ix_market_quotes_symbol', 'market_quotes', ['symbol'])
    op.create_index('ix_market_quotes_as_of', 'market_quotes', ['as_of'])
    op.create_index('ix_market_quotes_raw_payload_id', 'market_quotes', ['raw_payload_id'])
    op.create_index(
        'ix_market_quotes_org_symbol_as_of',
        'market_quotes',
        ['org_id', 'symbol', 'as_of'],
    )
    op.create_index(
        'uq_market_quotes_org_provider_symbol_as_of',
        'market_quotes',
        ['org_id', 'provider', 'symbol', 'as_of'],
        unique=True,
    )
    _enable_rls('market_quotes')


def downgrade() -> None:
    op.execute('DROP POLICY IF EXISTS market_quotes_tenant_isolation ON market_quotes;')
    op.drop_table('market_quotes')

    op.drop_index(
        'uq_market_timeseries_org_provider_symbol_timeframe_ts',
        table_name='market_timeseries',
    )
    op.drop_index('ix_market_timeseries_raw_payload_id', table_name='market_timeseries')
    op.drop_index('ix_market_timeseries_org_symbol_timeframe_ts', table_name='market_timeseries')
    op.drop_column('market_timeseries', 'fetched_at')
    op.drop_column('market_timeseries', 'raw_payload_id')
    op.drop_column('market_timeseries', 'schema_version')
    op.drop_column('market_timeseries', 'provider')
