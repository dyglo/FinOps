from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from finops_api.models import IntelRun
from finops_api.repositories.intel import IntelRepository
from finops_api.repositories.news_documents import NewsDocumentRepository
from finops_api.repositories.tool_call_audit import ToolCallAuditRepository
from finops_api.schemas.intel_runtime import (
    IntelClaim,
    IntelRunOutput,
    NewsSearchEvidence,
    NewsSearchToolInput,
    NewsSearchToolOutput,
)

ALLOWED_TOOLS = {'news_document_search'}


class IntelRuntimeError(Exception):
    pass


async def execute_intel_run(
    *,
    session: AsyncSession,
    run: IntelRun,
    org_id: UUID,
) -> IntelRun:
    intel_repo = IntelRepository(session)
    audit_repo = ToolCallAuditRepository(session)

    await intel_repo.mark_running(run)

    try:
        if run.execution_mode == 'replay':
            output = await _execute_replay_mode(
                session=session,
                run=run,
                org_id=org_id,
                audit_repo=audit_repo,
            )
        else:
            output = await _execute_live_mode(
                session=session,
                run=run,
                org_id=org_id,
                audit_repo=audit_repo,
            )

        return await intel_repo.mark_completed(run, output_payload=output.model_dump(mode='json'))
    except Exception as exc:
        await intel_repo.mark_failed(run, str(exc))
        raise


async def _execute_live_mode(
    *,
    session: AsyncSession,
    run: IntelRun,
    org_id: UUID,
    audit_repo: ToolCallAuditRepository,
) -> IntelRunOutput:
    tool_input = _build_live_tool_input(run)
    tool_output = await _run_news_document_search_tool(
        session=session,
        org_id=org_id,
        tool_input=tool_input,
    )

    citations = _collect_citations(tool_output)
    await _validate_citations(citations=citations)

    await audit_repo.create(
        org_id=org_id,
        run_id=run.id,
        tool_name=tool_input.tool_name,
        status='success',
        request_payload=tool_input.model_dump(mode='json'),
        response_payload=tool_output.model_dump(mode='json'),
        citations=citations,
    )

    claims = _build_claims(tool_output)
    summary = _build_summary(tool_output)
    return IntelRunOutput(
        execution_mode='live',
        summary=summary,
        claims=claims,
        citations=citations,
        tool_count=1,
    )


async def _execute_replay_mode(
    *,
    session: AsyncSession,
    run: IntelRun,
    org_id: UUID,
    audit_repo: ToolCallAuditRepository,
) -> IntelRunOutput:
    if run.replay_source_run_id is None:
        raise IntelRuntimeError('Replay mode requires replay_source_run_id')

    source_audits = await audit_repo.list_by_run_id(run_id=run.replay_source_run_id)
    if not source_audits:
        raise IntelRuntimeError('No source tool calls available for replay')

    replayed_tool_outputs: list[NewsSearchToolOutput] = []
    for source in source_audits:
        if source.tool_name not in ALLOWED_TOOLS:
            raise IntelRuntimeError(f'Tool not allowlisted for replay: {source.tool_name}')

        tool_input = NewsSearchToolInput.model_validate(source.request_payload)
        tool_output = NewsSearchToolOutput.model_validate(source.response_payload)
        replayed_tool_outputs.append(tool_output)

        citations = _collect_citations(tool_output)
        await audit_repo.create(
            org_id=org_id,
            run_id=run.id,
            tool_name=tool_input.tool_name,
            status='replayed',
            request_payload=tool_input.model_dump(mode='json'),
            response_payload=tool_output.model_dump(mode='json'),
            citations=citations,
        )

    primary_output = replayed_tool_outputs[0]
    citations = _collect_citations(primary_output)
    await _validate_citations(citations=citations)

    return IntelRunOutput(
        execution_mode='replay',
        summary=_build_summary(primary_output),
        claims=_build_claims(primary_output),
        citations=citations,
        tool_count=len(replayed_tool_outputs),
    )


def _build_live_tool_input(run: IntelRun) -> NewsSearchToolInput:
    payload = run.input_payload
    query = str(payload.get('query') or '').strip()
    if not query:
        query = run.input_snapshot_uri.strip()

    limit_raw = payload.get('limit', 5)
    if isinstance(limit_raw, bool):
        raise IntelRuntimeError('Invalid limit value')
    if isinstance(limit_raw, int):
        limit = limit_raw
    else:
        limit = int(str(limit_raw))
    job_id_raw = payload.get('job_id')
    job_id = UUID(str(job_id_raw)) if job_id_raw else None

    tool_name = str(payload.get('tool_name') or 'news_document_search')
    if tool_name not in ALLOWED_TOOLS:
        raise IntelRuntimeError(f'Tool not allowlisted: {tool_name}')

    return NewsSearchToolInput(
        tool_name='news_document_search',
        query=query,
        limit=limit,
        job_id=job_id,
    )


async def _run_news_document_search_tool(
    *,
    session: AsyncSession,
    org_id: UUID,
    tool_input: NewsSearchToolInput,
) -> NewsSearchToolOutput:
    news_repo = NewsDocumentRepository(session)
    rows = await news_repo.list_news(
        org_id=org_id,
        job_id=tool_input.job_id,
        q=tool_input.query,
        limit=tool_input.limit,
        offset=0,
    )

    documents = []
    for row in rows:
        citation = row.source_url.strip()
        documents.append(
            NewsSearchEvidence(
                title=row.title,
                source_url=row.source_url,
                snippet=row.snippet,
                published_at=row.published_at,
                citations=[citation] if citation else [],
            )
        )

    return NewsSearchToolOutput(documents=documents)


def _collect_citations(tool_output: NewsSearchToolOutput) -> list[str]:
    citations: list[str] = []
    seen: set[str] = set()
    for doc in tool_output.documents:
        for citation in doc.citations:
            clean = citation.strip()
            if clean and clean not in seen:
                seen.add(clean)
                citations.append(clean)
    return citations


async def _validate_citations(*, citations: list[str]) -> None:
    if not citations:
        raise IntelRuntimeError('Citations are required for web-derived claims')


def _build_claims(tool_output: NewsSearchToolOutput) -> list[IntelClaim]:
    claims: list[IntelClaim] = []
    for doc in tool_output.documents[:3]:
        claim = IntelClaim(
            claim=doc.title,
            citations=doc.citations,
        )
        if not claim.citations:
            raise IntelRuntimeError('Each claim must include at least one citation')
        claims.append(claim)

    return claims


def _build_summary(tool_output: NewsSearchToolOutput) -> str:
    if not tool_output.documents:
        return 'No matching documents were found for the requested query.'

    top_titles = [doc.title for doc in tool_output.documents[:3]]
    return f"Top documents: {' | '.join(top_titles)}"
