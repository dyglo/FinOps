from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text

from finops_api.db import SessionLocal
from finops_api.repositories.intel import IntelRepository
from finops_api.services.ingestion_pipeline import process_ingestion_job
from finops_api.services.intel_runtime import execute_intel_run


async def run_ingestion_job(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    job_id = UUID(str(payload['job_id']))
    org_id = UUID(str(payload['org_id']))
    redis_client = ctx['redis']

    result = await process_ingestion_job(job_id=job_id, org_id=org_id, redis_client=redis_client)
    result['pipeline'] = 'ingestion'
    result['processed_at'] = datetime.now(UTC).isoformat()
    return result


async def run_intel_analysis(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    run_id = UUID(str(payload['run_id']))
    org_id = UUID(str(payload['org_id']))

    async with SessionLocal() as session:
        await session.execute(
            text("SELECT set_config('app.current_org_id', :org_id, true)"),
            {'org_id': str(org_id)},
        )
        intel_repo = IntelRepository(session)
        run = await intel_repo.get(run_id)
        if run is None:
            raise ValueError(f'Intel run not found: {run_id}')

        executed = await execute_intel_run(session=session, run=run, org_id=org_id)
        return {
            'status': executed.status,
            'pipeline': 'intel',
            'run_id': str(executed.id),
            'execution_mode': executed.execution_mode,
            'processed_at': datetime.now(UTC).isoformat(),
        }


async def enqueue_embedding_refresh(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'status': 'completed',
        'pipeline': 'embeddings',
        'input': payload,
        'processed_at': datetime.now(UTC).isoformat(),
    }
