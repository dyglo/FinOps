"""phase1 schema versioning and retrieval indexes

Revision ID: 0004_phase1_schema_versioning
Revises: 0003_phase2_intel_runtime
Create Date: 2026-02-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_phase1_schema_versioning'
down_revision = '0003_phase2_intel_runtime'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'ingestion_jobs',
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='v1'),
    )
    op.add_column(
        'ingestion_raw_payloads',
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='v1'),
    )
    op.add_column(
        'news_documents',
        sa.Column(
            'normalization_version',
            sa.String(length=32),
            nullable=False,
            server_default='v1',
        ),
    )

    op.execute('ALTER TABLE ingestion_jobs ALTER COLUMN schema_version DROP DEFAULT;')
    op.execute('ALTER TABLE ingestion_raw_payloads ALTER COLUMN schema_version DROP DEFAULT;')
    op.execute('ALTER TABLE news_documents ALTER COLUMN normalization_version DROP DEFAULT;')

    op.create_index(
        'ix_ingestion_raw_payloads_org_fetched_at',
        'ingestion_raw_payloads',
        ['org_id', 'fetched_at'],
    )
    op.create_index('ix_news_documents_org_created_at', 'news_documents', ['org_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_news_documents_org_created_at', table_name='news_documents')
    op.drop_index('ix_ingestion_raw_payloads_org_fetched_at', table_name='ingestion_raw_payloads')

    op.drop_column('news_documents', 'normalization_version')
    op.drop_column('ingestion_raw_payloads', 'schema_version')
    op.drop_column('ingestion_jobs', 'schema_version')
