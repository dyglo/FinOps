from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class OrgScopedMixin:
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class IngestionJob(Base, OrgScopedMixin, TimestampMixin):
    __tablename__ = 'ingestion_jobs'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='queued')
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default='v1')
    attempt_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index(
            'uq_ingestion_jobs_org_provider_resource_idempotency',
            'org_id',
            'provider',
            'resource',
            'idempotency_key',
            unique=True,
        ),
    )


class IngestionRawPayload(Base, OrgScopedMixin):
    __tablename__ = 'ingestion_raw_payloads'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False, default='v1')
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    response_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    http_status: Mapped[int | None] = mapped_column(nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_ingestion_raw_payloads_org_job', 'org_id', 'job_id'),
        Index('ix_ingestion_raw_payloads_org_content_hash', 'org_id', 'content_hash'),
        Index('ix_ingestion_raw_payloads_org_fetched_at', 'org_id', 'fetched_at'),
        Index(
            'uq_ingestion_raw_payloads_org_provider_content_hash',
            'org_id',
            'provider',
            'content_hash',
            unique=True,
        ),
    )


class NewsDocument(Base, OrgScopedMixin):
    __tablename__ = 'news_documents'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    raw_payload_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    source_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    normalization_version: Mapped[str] = mapped_column(String(32), nullable=False, default='v1')
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(String(256), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_news_documents_org_job', 'org_id', 'job_id'),
        Index('ix_news_documents_org_published_at', 'org_id', 'published_at'),
        Index('ix_news_documents_org_created_at', 'org_id', 'created_at'),
        Index(
            'uq_news_documents_org_provider_url_document_hash',
            'org_id',
            'source_provider',
            'source_url',
            'document_hash',
            unique=True,
        ),
    )


class IntelRun(Base, OrgScopedMixin, TimestampMixin):
    __tablename__ = 'intel_runs'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    run_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='pending')
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False)
    input_snapshot_uri: Mapped[str] = mapped_column(Text, nullable=False)
    input_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    graph_version: Mapped[str] = mapped_column(String(32), nullable=False, default='v1')
    execution_mode: Mapped[str] = mapped_column(String(16), nullable=False, default='live')
    replay_source_run_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    output_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ToolCallAudit(Base, OrgScopedMixin):
    __tablename__ = 'tool_call_audit'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    response_payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    citations: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MarketTimeseries(Base, OrgScopedMixin):
    __tablename__ = 'market_timeseries'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (Index('ix_market_timeseries_org_symbol_ts', 'org_id', 'symbol', 'ts'),)


class SignalFeature(Base, OrgScopedMixin, TimestampMixin):
    __tablename__ = 'signal_features'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    feature_name: Mapped[str] = mapped_column(String(128), nullable=False)
    feature_version: Mapped[str] = mapped_column(String(32), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    meta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class EmbeddingDocument(Base, OrgScopedMixin, TimestampMixin):
    __tablename__ = 'embedding_documents'

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
