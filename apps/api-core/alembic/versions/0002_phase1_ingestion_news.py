"""phase1 ingestion raw payload and news documents

Revision ID: 0002_phase1_ingestion_news
Revises: 0001_initial
Create Date: 2026-02-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_phase1_ingestion_news'
down_revision = '0001_initial'
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
    op.add_column('ingestion_jobs', sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('ingestion_jobs', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    op.execute('ALTER TABLE ingestion_jobs ALTER COLUMN attempt_count DROP DEFAULT;')

    op.drop_constraint('ingestion_jobs_idempotency_key_key', 'ingestion_jobs', type_='unique')
    op.create_index(
        'uq_ingestion_jobs_org_provider_resource_idempotency',
        'ingestion_jobs',
        ['org_id', 'provider', 'resource', 'idempotency_key'],
        unique=True,
    )

    op.create_table(
        'ingestion_raw_payloads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=64), nullable=False),
        sa.Column('resource', sa.String(length=128), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('request_payload', sa.JSON(), nullable=False),
        sa.Column('response_payload', sa.JSON(), nullable=False),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('provider_request_id', sa.String(length=128), nullable=True),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_ingestion_raw_payloads_org_id', 'ingestion_raw_payloads', ['org_id'])
    op.create_index('ix_ingestion_raw_payloads_job_id', 'ingestion_raw_payloads', ['job_id'])
    op.create_index('ix_ingestion_raw_payloads_org_job', 'ingestion_raw_payloads', ['org_id', 'job_id'])
    op.create_index(
        'ix_ingestion_raw_payloads_org_content_hash',
        'ingestion_raw_payloads',
        ['org_id', 'content_hash'],
    )
    op.create_index(
        'uq_ingestion_raw_payloads_org_provider_content_hash',
        'ingestion_raw_payloads',
        ['org_id', 'provider', 'content_hash'],
        unique=True,
    )

    op.create_table(
        'news_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('raw_payload_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_provider', sa.String(length=64), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('snippet', sa.Text(), nullable=False),
        sa.Column('author', sa.String(length=256), nullable=True),
        sa.Column('language', sa.String(length=16), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('document_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_news_documents_org_id', 'news_documents', ['org_id'])
    op.create_index('ix_news_documents_job_id', 'news_documents', ['job_id'])
    op.create_index('ix_news_documents_raw_payload_id', 'news_documents', ['raw_payload_id'])
    op.create_index('ix_news_documents_org_job', 'news_documents', ['org_id', 'job_id'])
    op.create_index('ix_news_documents_org_published_at', 'news_documents', ['org_id', 'published_at'])
    op.create_index(
        'uq_news_documents_org_provider_url_document_hash',
        'news_documents',
        ['org_id', 'source_provider', 'source_url', 'document_hash'],
        unique=True,
    )

    _enable_rls('ingestion_raw_payloads')
    _enable_rls('news_documents')


def downgrade() -> None:
    op.execute('DROP POLICY IF EXISTS news_documents_tenant_isolation ON news_documents;')
    op.execute('DROP POLICY IF EXISTS ingestion_raw_payloads_tenant_isolation ON ingestion_raw_payloads;')

    op.drop_table('news_documents')
    op.drop_table('ingestion_raw_payloads')

    op.drop_index('uq_ingestion_jobs_org_provider_resource_idempotency', table_name='ingestion_jobs')
    op.create_unique_constraint('ingestion_jobs_idempotency_key_key', 'ingestion_jobs', ['idempotency_key'])

    op.drop_column('ingestion_jobs', 'completed_at')
    op.drop_column('ingestion_jobs', 'started_at')
    op.drop_column('ingestion_jobs', 'error_message')
    op.drop_column('ingestion_jobs', 'attempt_count')