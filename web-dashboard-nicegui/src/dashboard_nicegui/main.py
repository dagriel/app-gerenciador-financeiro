from __future__ import annotations

from nicegui import app, ui

from dashboard_nicegui.api_client.client import close_finance_api, init_finance_api
from dashboard_nicegui.core.logging import setup_logging
from dashboard_nicegui.core.settings import Settings
from dashboard_nicegui.features.accounts.page import accounts_page
from dashboard_nicegui.features.budgets.page import budgets_page
from dashboard_nicegui.features.categories.page import categories_page
from dashboard_nicegui.features.dashboard.page import dashboard_page
from dashboard_nicegui.features.transactions.page import transactions_page

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


@app.on_startup  # type: ignore[attr-defined]
async def _startup() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    await init_finance_api(
        base_url=str(settings.fin_api_base_url),
        api_key=settings.fin_api_key,
    )


@app.on_shutdown  # type: ignore[attr-defined]
async def _shutdown() -> None:
    await close_finance_api()


def _register_routes() -> None:
    # Importante: importar/registrar páginas aqui evita efeitos colaterais em import time.
    dashboard_page()
    transactions_page()
    budgets_page()
    accounts_page()
    categories_page()


def run() -> None:
    """Executa o Dashboard NiceGUI."""
    settings = get_settings()

    _register_routes()

    ui.run(
        title="Dashboard Financeiro (NiceGUI)",
        port=settings.dashboard_port,
        reload=False,
        show=False,
    )
