from __future__ import annotations

from nicegui import ui

from dashboard_nicegui.shared.components import page_shell


def transactions_page() -> None:
    @ui.page("/transactions")
    async def _page() -> None:
        with page_shell(title="Transações"):
            ui.label("Em construção (MVP): listagem + criação + exclusão.").classes("text-subtitle1")
            ui.markdown(
                """
**Próximos passos desta página**
- Lista com filtros (from/to, conta, categoria, kind)
- Criar receita / despesa / transferência
- Excluir transação (transfer remove o par)
                """.strip()
            )
