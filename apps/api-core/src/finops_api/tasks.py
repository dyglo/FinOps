from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


async def run_ingestion_job(ctx: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'status': 'completed',
        'pipeline': 'ingestion',
        'received': payload,
        'processed_at': datetime.now(UTC).isoformat(),
    }


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
