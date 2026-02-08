from __future__ import annotations

from uuid import UUID

from arq import create_pool
from arq.connections import RedisSettings

from finops_api.config import get_settings


async def enqueue_ingestion_job(*, job_id: UUID, org_id: UUID) -> None:
    settings = get_settings()
    redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await redis_pool.enqueue_job(
            'run_ingestion_job',
            {'job_id': str(job_id), 'org_id': str(org_id)},
            _queue_name='q.agent.async',
        )
    finally:
        await redis_pool.close()