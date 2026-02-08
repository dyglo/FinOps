"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-08
"""

from __future__ import annotations

from alembic import op
from pgvector.sqlalchemy import Vector
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
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
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')

    op.create_table(
        'ingestion_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('resource', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=False, unique=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ingestion_jobs_org_id', 'ingestion_jobs', ['org_id'])

    op.create_table(
        'intel_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('model_name', sa.String(length=128), nullable=False),
        sa.Column('prompt_version', sa.String(length=64), nullable=False),
        sa.Column('input_snapshot_uri', sa.Text(), nullable=False),
        sa.Column('output_payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_intel_runs_org_id', 'intel_runs', ['org_id'])

    op.create_table(
        'tool_call_audit',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('request_payload', sa.JSON(), nullable=False),
        sa.Column('response_payload', sa.JSON(), nullable=False),
        sa.Column('citations', postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tool_call_audit_org_id', 'tool_call_audit', ['org_id'])
    op.create_index('ix_tool_call_audit_run_id', 'tool_call_audit', ['run_id'])

    op.create_table(
        'market_timeseries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('timeframe', sa.String(length=16), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
    )
    op.create_index('ix_market_timeseries_org_id', 'market_timeseries', ['org_id'])
    op.create_index('ix_market_timeseries_symbol', 'market_timeseries', ['symbol'])
    op.create_index('ix_market_timeseries_ts', 'market_timeseries', ['ts'])
    op.create_index('ix_market_timeseries_org_symbol_ts', 'market_timeseries', ['org_id', 'symbol', 'ts'])

    op.create_table(
        'signal_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=32), nullable=False),
        sa.Column('feature_name', sa.String(length=128), nullable=False),
        sa.Column('feature_version', sa.String(length=32), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_signal_features_org_id', 'signal_features', ['org_id'])
    op.create_index('ix_signal_features_symbol', 'signal_features', ['symbol'])

    op.create_table(
        'embedding_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.String(length=64), nullable=False),
        sa.Column('source_ref', sa.String(length=256), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('embedding_model', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_embedding_documents_org_id', 'embedding_documents', ['org_id'])

    _enable_rls('ingestion_jobs')
    _enable_rls('intel_runs')
    _enable_rls('tool_call_audit')
    _enable_rls('market_timeseries')
    _enable_rls('signal_features')
    _enable_rls('embedding_documents')


def downgrade() -> None:
    tables = [
        'embedding_documents',
        'signal_features',
        'market_timeseries',
        'tool_call_audit',
        'intel_runs',
        'ingestion_jobs',
    ]

    for table in tables:
        op.execute(f'DROP POLICY IF EXISTS {table}_tenant_isolation ON {table};')
        op.drop_table(table)
