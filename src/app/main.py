"""Main FastAPI application factory and setup."""

from fastapi import Depends, FastAPI

from app.api.deps import require_api_key
from app.api.routers import accounts, budgets, categories, reports, transactions
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    setup_logging()

    app = FastAPI(
        title="APP-GERENCIADOR-FINANCEIRO",
        version="0.1.0",
        description="MVP API-only para controle financeiro pessoal (single-user local)",
    )

    @app.get("/health")
    def health() -> dict:
        """Health check endpoint."""
        return {"status": "ok"}

    # Include all routers with API key protection
    app.include_router(accounts.router, dependencies=[Depends(require_api_key)])
    app.include_router(categories.router, dependencies=[Depends(require_api_key)])
    app.include_router(transactions.router, dependencies=[Depends(require_api_key)])
    app.include_router(budgets.router, dependencies=[Depends(require_api_key)])
    app.include_router(reports.router, dependencies=[Depends(require_api_key)])

    return app


app = create_app()
