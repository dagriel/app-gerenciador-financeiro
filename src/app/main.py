"""Main FastAPI application factory and setup."""

from __future__ import annotations

from http import HTTPStatus

from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.deps import require_api_key
from app.api.openapi import custom_openapi
from app.api.routers import accounts, budgets, categories, reports, transactions
from app.domain.error_messages import ErrorMessage
from app.domain.errors import (
    BadRequestError,
    ConflictError,
    DomainError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.logging import setup_logging
from app.schemas.errors import ProblemDetail


class HealthOut(BaseModel):
    status: str


def _http_status_for_domain_error(exc: DomainError) -> int:
    if isinstance(exc, BadRequestError):
        return 400
    if isinstance(exc, UnauthorizedError):
        return 401
    if isinstance(exc, NotFoundError):
        return 404
    if isinstance(exc, ConflictError):
        return 409
    # Fallback (unknown domain error type)
    return 400


def _problem_detail(
    *,
    status_code: int,
    detail: str,
    request: Request,
    code: str | None = None,
    errors: list[dict[str, object]] | None = None,
) -> dict:
    # Keep titles stable across Python versions (Python 3.13 uses "Unprocessable Content" for 422).
    if status_code == 422:
        title = "Unprocessable Entity"
    else:
        try:
            title = HTTPStatus(status_code).phrase
        except ValueError:
            title = "Error"

    payload = ProblemDetail(
        status=status_code,
        title=title,
        detail=detail,
        code=code,
        instance=request.url.path,
        errors=errors,
    )
    # Ensure nested values (e.g., Decimal in validation errors) are JSON-serializable.
    return jsonable_encoder(payload.model_dump(exclude_none=True))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    openapi_tags = [
        {"name": "accounts", "description": "Gestão de contas (banco/carteira)."},
        {"name": "categories", "description": "Gestão de categorias (receita/despesa)."},
        {"name": "transactions", "description": "Lançamentos (receita/despesa) e transferências."},
        {
            "name": "budgets",
            "description": "Orçamentos mensais por categoria (MVP: apenas despesas).",
        },
        {"name": "reports", "description": "Relatórios e consolidações mensais."},
    ]

    app = FastAPI(
        title="APP-GERENCIADOR-FINANCEIRO",
        version="0.1.0",
        description="MVP API-only para controle financeiro pessoal (single-user local)",
        openapi_tags=openapi_tags,
        servers=[{"url": "http://localhost:8000", "description": "Local"}]
    )

    # Enrich Swagger/OpenAPI with common error responses + realistic examples
    app.openapi = lambda: custom_openapi(app)  # type: ignore[method-assign]

    @app.exception_handler(DomainError)
    def domain_error_handler(request: Request, exc: DomainError):  # type: ignore[override]
        status_code = _http_status_for_domain_error(exc)
        return JSONResponse(
            status_code=status_code,
            content=_problem_detail(
                status_code=status_code,
                detail=exc.detail_str,
                code=exc.code,
                request=request,
                errors=exc.errors,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    def http_exception_handler(request: Request, exc: StarletteHTTPException):  # type: ignore[override]
        error_code: str | None = None

        if isinstance(exc.detail, ErrorMessage):
            error_code = exc.detail.name
            detail = exc.detail.value
        elif isinstance(exc.detail, str):
            detail = exc.detail
        else:
            detail = str(exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content=_problem_detail(
                status_code=exc.status_code,
                detail=detail,
                code=error_code,
                request=request,
            ),
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore[override]
        return JSONResponse(
            status_code=422,
            content=_problem_detail(
                status_code=422,
                detail="Erro de validação",
                code="REQUEST_VALIDATION_ERROR",
                request=request,
                errors=list(exc.errors()),
            ),
        )

    @app.get("/health", response_model=HealthOut, tags=["health"])
    def health() -> dict:
        """Health check endpoint (no authentication)."""
        return {"status": "ok"}

    # Include all routers with API key protection
    app.include_router(accounts.router, dependencies=[Depends(require_api_key)])
    app.include_router(categories.router, dependencies=[Depends(require_api_key)])
    app.include_router(transactions.router, dependencies=[Depends(require_api_key)])
    app.include_router(budgets.router, dependencies=[Depends(require_api_key)])
    app.include_router(reports.router, dependencies=[Depends(require_api_key)])

    return app


app = create_app()
