from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['health'])


@router.get('/live')
async def live() -> dict[str, str]:
    return {'status': 'ok'}


@router.get('/ready')
async def ready() -> dict[str, str]:
    return {'status': 'ready', 'timestamp': datetime.now(tz=UTC).isoformat()}
