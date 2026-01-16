from __future__ import annotations

from nicegui import ui

from dashboard_nicegui.shared.components import page_shell


def budgets_page() -> None:
    @ui.page("/budgets")
    async def _page() -> None:
        with page_shell(title="Orçamentos"):
            ui.label("Em construção (MVP): listar e upsert por mês/categoria.").classes(
                "text-subtitle1"
            )
            ui.markdown(
                """
**Próximos passos desta página**
- Seletor de mês (YYYY-MM)
- Listar budgets do mês (`GET /budgets?month=...`)
- Upsert (`POST /budgets`) com validação (somente categorias EXPENSE)
                """.strip()
            )
