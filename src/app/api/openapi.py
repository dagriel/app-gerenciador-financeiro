"""OpenAPI helpers (documentation utilities).

This module centralizes common response documentation to keep routers concise and
consistent, especially for standardized error payloads.

It also provides a `custom_openapi(app)` generator to enrich the Swagger with:
- Common error responses across operations (401/405/422)
- 404 for resource endpoints (paths containing `{...}`), when applicable
- Realistic examples using the project's `ProblemDetail` contract
"""

from __future__ import annotations

from collections.abc import Iterable
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.schemas.errors import ProblemDetail

# Keep titles/descriptions stable across Python versions.
# (Python 3.13 uses "Unprocessable Content" for 422; most API docs expect "Unprocessable Entity".)
_HTTP_PHRASE_OVERRIDES: dict[int, str] = {422: "Unprocessable Entity"}


def _http_phrase(code: int) -> str:
    override = _HTTP_PHRASE_OVERRIDES.get(code)
    if override is not None:
        return override
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "Error"


def _problem_detail_value(
    *,
    status: int,
    title: str | None = None,
    detail: str,
    code: str | None = None,
    instance: str,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a realistic example value following our ProblemDetail contract."""
    value: dict[str, Any] = {
        "status": status,
        "title": title or _http_phrase(status),
        "detail": detail,
        "instance": instance,
    }
    if code is not None:
        value["code"] = code
    if errors is not None:
        value["errors"] = errors
    return value


# Reusable examples (also used by `custom_openapi`).
PROBLEM_DETAIL_EXAMPLES: dict[int, dict[str, Any]] = {
    400: {
        "business_rule": {
            "summary": "Regra de negócio / validação manual",
            "value": _problem_detail_value(
                status=400,
                detail="Informe from_date e to_date juntos",
                code="TX_FROM_TO_BOTH_REQUIRED",
                instance="/transactions",
            ),
        }
    },
    401: {
        "api_key_invalid": {
            "summary": "API key inválida (ou ausente quando habilitada)",
            "value": _problem_detail_value(
                status=401,
                detail="API key inválida",
                code="API_KEY_INVALID",
                instance="/accounts",
            ),
        }
    },
    404: {
        "resource_not_found": {
            "summary": "Recurso não encontrado (ex.: conta inexistente)",
            "value": _problem_detail_value(
                status=404,
                detail="Conta não encontrada",
                code="ACCOUNT_NOT_FOUND",
                instance="/accounts/999",
            ),
        }
    },
    405: {
        "method_not_allowed": {
            "summary": "Método não permitido",
            "value": _problem_detail_value(
                status=405,
                detail="Method Not Allowed",
                instance="/accounts",
            ),
        }
    },
    409: {
        "conflict": {
            "summary": "Conflito (ex.: categoria duplicada)",
            "value": _problem_detail_value(
                status=409,
                detail="Categoria já existe",
                code="CATEGORY_ALREADY_EXISTS",
                instance="/categories",
            ),
        }
    },
    422: {
        "request_validation_error_body": {
            "summary": "Erro de validação (body) — Pydantic",
            "value": _problem_detail_value(
                status=422,
                detail="Erro de validação",
                code="REQUEST_VALIDATION_ERROR",
                instance="/accounts",
                errors=[
                    {
                        "loc": ["body", "name"],
                        "msg": "String should have at least 1 character",
                        "type": "string_too_short",
                    }
                ],
            ),
        },
        "request_validation_error_query": {
            "summary": "Erro de validação (query) — Pydantic",
            "value": _problem_detail_value(
                status=422,
                detail="Erro de validação",
                code="REQUEST_VALIDATION_ERROR",
                instance="/reports/monthly-summary",
                errors=[
                    {
                        "loc": ["query", "month"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ],
            ),
        },
    },
}


def error_responses(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    """Build a FastAPI `responses={...}` dict for common error status codes.

    Example:
        responses=error_responses(400, 401, 404)

    Notes:
        - Each response uses the `ProblemDetail` model.
        - When available, we attach a realistic example based on observed runtime behavior.
    """
    responses: dict[int | str, dict[str, Any]] = {}
    for code in status_codes:
        resp: dict[str, Any] = {
            "model": ProblemDetail,
            "description": _http_phrase(code),
        }

        examples = PROBLEM_DETAIL_EXAMPLES.get(code)
        if examples:
            resp["content"] = {"application/json": {"examples": examples}}

        responses[code] = resp

    return responses


def _problem_detail_response_obj(status_code: int) -> dict[str, Any]:
    """OpenAPI response object for ProblemDetail with examples (used in custom_openapi)."""
    obj: dict[str, Any] = {
        "description": _http_phrase(status_code),
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ProblemDetail"},
            }
        },
    }
    examples = PROBLEM_DETAIL_EXAMPLES.get(status_code)
    if examples:
        obj["content"]["application/json"]["examples"] = examples
    return obj


def apply_common_error_responses(
    openapi_schema: dict[str, Any],
    *,
    common_status_codes: Iterable[int] = (401, 405, 422),
    include_404_for_param_paths: bool = True,
) -> dict[str, Any]:
    """Enrich every operation with common error responses.

    Why:
        Some errors (notably 405 and 422) are produced by the framework layer and won't
        show up in endpoint-level `responses=...`. Also, most operations require the
        API key (401).

        We avoid adding 404 to every operation because "route not found" is not an
        operation-level concern. Instead, we ensure 404 is present on paths with path
        params (resource not found).

    Behavior:
        - Adds 401/405/422 to all operations except `/health`.
        - Ensures 404 is present on paths containing `{` (i.e., path params).

    We intentionally avoid overriding existing responses defined at the endpoint level.
    """
    paths: dict[str, Any] = openapi_schema.get("paths", {})

    for path, methods in paths.items():
        if path == "/health":
            continue

        has_path_param = "{" in path and "}" in path
        for method, operation in methods.items():
            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
            }:
                continue

            responses: dict[str, Any] = operation.setdefault("responses", {})

            for status_code in common_status_codes:
                key = str(status_code)
                responses.setdefault(key, _problem_detail_response_obj(status_code))

            # 404 for resource-not-found on parameterized paths (e.g., /accounts/{account_id}).
            if include_404_for_param_paths and has_path_param:
                responses.setdefault("404", _problem_detail_response_obj(404))

    return openapi_schema


def custom_openapi(app: FastAPI) -> dict[str, Any]:
    """Custom OpenAPI schema generator.

    Adds examples and common error responses to improve documentation quality.

    Usage:
        app.openapi = lambda: custom_openapi(app)
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=app.description,
        tags=app.openapi_tags,
        servers=app.servers,
    )

    apply_common_error_responses(schema)

    app.openapi_schema = schema
    return app.openapi_schema
