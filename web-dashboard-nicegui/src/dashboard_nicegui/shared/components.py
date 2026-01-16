from __future__ import annotations

from contextlib import contextmanager

from nicegui import ui


def nav_menu() -> None:
    """Menu lateral padrão (navegação do app)."""
    ui.link("Dashboard", "/dashboard").classes("text-white")
    ui.link("Transações", "/transactions").classes("text-white")
    ui.link("Orçamentos", "/budgets").classes("text-white")
    ui.link("Contas", "/accounts").classes("text-white")
    ui.link("Categorias", "/categories").classes("text-white")


@contextmanager
def page_shell(*, title: str):
    """Layout base por página (header + drawer + container).

    NiceGUI cria UI por rota; esse shell mantém consistência visual e navegação.
    """
    with ui.header().classes("bg-primary text-white"):
        ui.label("Gerenciador Financeiro").classes("text-h6")
        ui.space()
        ui.label(title)

    # NiceGUI 3.x exige informar o lado do drawer ("left" | "right").
    with ui.drawer("left").classes("bg-grey-9"):
        nav_menu()

    with ui.column().classes("p-4 gap-4"):
        yield


def notify_error(message: str) -> None:
    ui.notify(message, type="negative", close_button=True)


def notify_success(message: str) -> None:
    ui.notify(message, type="positive", close_button=True)
