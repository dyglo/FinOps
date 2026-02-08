from __future__ import annotations

from arq.connections import RedisSettings

from finops_api.config import get_settings
from finops_api.tasks import (
    enqueue_embedding_refresh,
    run_ingestion_job,
    run_intel_analysis,
)

settings = get_settings()


class WorkerSettings:
    functions = [run_ingestion_job, run_intel_analysis, enqueue_embedding_refresh]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = settings.worker_max_jobs
    queue_name = 'q.agent.async'