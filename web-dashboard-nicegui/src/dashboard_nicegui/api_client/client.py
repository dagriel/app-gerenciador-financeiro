from __future__ import annotations

import logging
from typing import Any

import httpx

from dashboard_nicegui.api_client.dtos import MonthlySummaryOut
from dashboard_nicegui.core.errors import (
    ApiProblemError,
    ApiUnexpectedResponseError,
    try_parse_problem_detail,
)

logger = logging.getLogger(__name__)

_fin_client: httpx.AsyncClient | None = None


def _require_client() -> httpx.AsyncClient:
    if _fin_client is None:
        raise RuntimeError("Finance API client não inicializado. (init_finance_api não foi chamado)")
    return _fin_client


async def init_finance_api(*, base_url: str, api_key: str) -> None:
    """Inicializa o AsyncClient usado para falar com a API financeira."""
    global _fin_client

    # Re-init idempotente (útil em reload/testes).
    if _fin_client is not None:
        await _fin_client.aclose()
        _fin_client = None

    _fin_client = httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(10.0),
        headers={"X-API-Key": api_key},
    )


async def close_finance_api() -> None:
    global _fin_client
    if _fin_client is not None:
        await _fin_client.aclose()
        _fin_client = None


async def _request_json(method: str, url: str, *, params: dict[str, Any] | None = None) -> Any:
    client = _require_client()

    try:
        resp = await client.request(method, url, params=params)
    except httpx.RequestError as exc:
        logger.exception("Erro de rede ao chamar API: %s %s", method, url)
        raise RuntimeError(f"Falha de rede ao chamar a API: {exc}") from exc

    # HTTP error -> tenta parsear ProblemDetail
    if resp.is_error:
        try:
            data = resp.json()
        except Exception:
            raise ApiUnexpectedResponseError(
                status_code=resp.status_code,
                body_excerpt=(resp.text or "")[:500],
            )

        problem = try_parse_problem_detail(data)
        if problem is not None:
            raise ApiProblemError(problem)

        raise ApiUnexpectedResponseError(
            status_code=resp.status_code,
            body_excerpt=str(data)[:500],
        )

    # Success -> json parse
    try:
        return resp.json()
    except Exception as exc:
        raise ApiUnexpectedResponseError(
            status_code=resp.status_code,
            body_excerpt=(resp.text or "")[:500],
        ) from exc


async def get_monthly_summary(*, month: str) -> MonthlySummaryOut:
    data = await _request_json("GET", "/reports/monthly-summary", params={"month": month})
    try:
        return MonthlySummaryOut.model_validate(data)
    except Exception as exc:
        raise ApiUnexpectedResponseError(
            status_code=200,
            body_excerpt=str(data)[:500],
        ) from exc
