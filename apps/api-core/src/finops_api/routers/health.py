from datetime import UTC, datetime

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter
from sqlalchemy import text

from finops_api.config import get_settings
from finops_api.db import SessionLocal

router = APIRouter(prefix='/health', tags=['health'])


@router.get('/live')
async def live() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/ready')
async def ready() -> dict[str, object]:
    settings = get_settings()

    db_ready = False
    redis_ready = False

    try:
        async with SessionLocal() as session:
            await session.execute(text('SELECT 1'))
        db_ready = True
    except Exception:
        db_ready = False

    redis_pool = None
    try:
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        await redis_pool.ping()
        redis_ready = True
    except Exception:
        redis_ready = False
    finally:
        if redis_pool is not None:
            await redis_pool.close()

    status = 'ready' if db_ready and redis_ready else 'degraded'
    return {
        'status': status,
        'timestamp': datetime.now(tz=UTC).isoformat(),
        'checks': {'database': db_ready, 'redis': redis_ready},
    }
