"""phase2 intel deterministic runtime fields

Revision ID: 0003_phase2_intel_runtime
Revises: 0002_phase1_ingestion_news
Create Date: 2026-02-08
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_phase2_intel_runtime'
down_revision = '0002_phase1_ingestion_news'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('intel_runs', sa.Column('input_payload', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('intel_runs', sa.Column('graph_version', sa.String(length=32), nullable=False, server_default='v1'))
    op.add_column('intel_runs', sa.Column('execution_mode', sa.String(length=16), nullable=False, server_default='live'))
    op.add_column('intel_runs', sa.Column('replay_source_run_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('intel_runs', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('intel_runs', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    op.execute('ALTER TABLE intel_runs ALTER COLUMN input_payload DROP DEFAULT;')
    op.execute('ALTER TABLE intel_runs ALTER COLUMN graph_version DROP DEFAULT;')
    op.execute('ALTER TABLE intel_runs ALTER COLUMN execution_mode DROP DEFAULT;')

    op.create_index('ix_intel_runs_replay_source_run_id', 'intel_runs', ['replay_source_run_id'])


def downgrade() -> None:
    op.drop_index('ix_intel_runs_replay_source_run_id', table_name='intel_runs')
    op.drop_column('intel_runs', 'completed_at')
    op.drop_column('intel_runs', 'error_message')
    op.drop_column('intel_runs', 'replay_source_run_id')
    op.drop_column('intel_runs', 'execution_mode')
    op.drop_column('intel_runs', 'graph_version')
    op.drop_column('intel_runs', 'input_payload')