from __future__ import annotations

from nicegui import ui

from dashboard_nicegui.shared.components import page_shell


def accounts_page() -> None:
    @ui.page("/accounts")
    async def _page() -> None:
        with page_shell(title="Contas"):
            ui.label("Em construção (MVP): listar, criar, editar e desativar contas.").classes(
                "text-subtitle1"
            )
            ui.markdown(
                """
**Próximos passos desta página**
- Listar contas (toggle incluir inativas): `GET /accounts?include_inactive=true|false`
- Criar: `POST /accounts`
- Editar: `PUT /accounts/{id}`
- Desativar: `DELETE /accounts/{id}` (soft delete)
                """.strip()
            )
