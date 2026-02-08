from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from finops_api.services.ingestion_pipeline import process_ingestion_job


async def run_ingestion_job(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    job_id = UUID(str(payload['job_id']))
    org_id = UUID(str(payload['org_id']))
    redis_client = ctx['redis']

    result = await process_ingestion_job(job_id=job_id, org_id=org_id, redis_client=redis_client)
    result['pipeline'] = 'ingestion'
    result['processed_at'] = datetime.now(UTC).isoformat()
    return result


async def run_intel_analysis(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'status': 'completed',
        'pipeline': 'intel',
        'input': payload,
        'note': 'Deterministic orchestration stub. Attach tool calls and citations here.',
        'processed_at': datetime.now(UTC).isoformat(),
    }


async def enqueue_embedding_refresh(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'status': 'completed',
        'pipeline': 'embeddings',
        'input': payload,
        'processed_at': datetime.now(UTC).isoformat(),
    }
