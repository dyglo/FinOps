from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from finops_api.config import get_settings
from finops_api.logging_config import configure_logging
from finops_api.routers.documents import router as documents_router
from finops_api.routers.health import router as health_router
from finops_api.routers.ingestion import router as ingestion_router
from finops_api.routers.intel import router as intel_router
from finops_api.routers.market import router as market_router
from finops_api.routers.signals import router as signals_router
from finops_api.routers.system import router as system_router

settings = get_settings()
request_logger = logging.getLogger('finops_api.request')


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


app = FastAPI(title='FinOps API Core', version='0.1.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',') if origin.strip()],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def request_context_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    request.state.request_id = request.headers.get('X-Request-Id', str(uuid4()))
    request.state.trace_id = request.headers.get('X-Trace-Id', request.state.request_id)
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers['X-Request-Id'] = request.state.request_id
    response.headers['X-Trace-Id'] = request.state.trace_id
    response.headers['X-Response-Time-Ms'] = f'{elapsed:.2f}'
    response.headers['X-Served-At'] = datetime.now(UTC).isoformat()
    request_logger.info(
        'request_completed',
        extra={
            'request_id': request.state.request_id,
            'trace_id': request.state.trace_id,
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'response_time_ms': round(elapsed, 2),
        },
    )
    return response


app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(intel_router)
app.include_router(market_router)
app.include_router(documents_router)
app.include_router(signals_router)
app.include_router(system_router)
