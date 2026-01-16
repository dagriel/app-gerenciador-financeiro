from __future__ import annotations

from nicegui import ui

from dashboard_nicegui.shared.components import page_shell


def categories_page() -> None:
    @ui.page("/categories")
    async def _page() -> None:
        with page_shell(title="Categorias"):
            ui.label("Em construção (MVP): listar, criar, editar e desativar categorias.").classes(
                "text-subtitle1"
            )
            ui.markdown(
                """
**Próximos passos desta página**
- Listar categorias (toggle incluir inativas): `GET /categories?include_inactive=true|false`
- Criar: `POST /categories`
- Editar: `PUT /categories/{id}`
- Desativar: `DELETE /categories/{id}` (soft delete)
                """.strip()
            )
