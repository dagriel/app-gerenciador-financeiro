from __future__ import annotations

import logging

from nicegui import ui

from dashboard_nicegui.api_client.client import get_monthly_summary
from dashboard_nicegui.core.errors import ApiProblemError, map_problem_code_to_user_message
from dashboard_nicegui.shared.components import notify_error, page_shell
from dashboard_nicegui.shared.formatters import last_n_months, money_fmt_brl, today_month

logger = logging.getLogger(__name__)


def dashboard_page() -> None:
    @ui.page("/")
    async def _index() -> None:
        ui.navigate.to("/dashboard")

    @ui.page("/dashboard")
    async def _page() -> None:
        with page_shell(title="Dashboard (Resumo mensal)"):
            months = last_n_months(12, from_month=today_month())

            ui.label("Mês").classes("text-subtitle1")
            month_select = ui.select(months, value=months[0]).props("outlined dense")

            header_row = ui.row().classes("gap-2 items-center")
            status_row = ui.row().classes("items-center gap-2")

            with ui.row().classes("gap-4"):
                income_card = ui.card().classes("p-4 w-64")
                expense_card = ui.card().classes("p-4 w-64")
                balance_card = ui.card().classes("p-4 w-64")

            by_cat_table_container = ui.column().classes("w-full")

            async def render() -> None:
                # Limpa área
                income_card.clear()
                expense_card.clear()
                balance_card.clear()
                status_row.clear()
                by_cat_table_container.clear()

                with status_row:
                    ui.spinner(size="sm")
                    ui.label("Carregando...")

                try:
                    report = await get_monthly_summary(month=str(month_select.value))
                except ApiProblemError as exc:
                    status_row.clear()
                    msg = exc.problem.detail
                    if exc.problem.code:
                        msg = map_problem_code_to_user_message(exc.problem.code) or msg
                    notify_error(msg)
                    logger.info("ProblemDetail: %s", exc.problem.model_dump())
                    return
                except Exception as exc:
                    status_row.clear()
                    notify_error(str(exc))
                    logger.exception("Erro inesperado ao buscar relatório")
                    return

                status_row.clear()

                with income_card:
                    ui.label("Receitas").classes("text-grey-7")
                    ui.label(money_fmt_brl(report.income_total)).classes("text-h6")

                with expense_card:
                    ui.label("Despesas").classes("text-grey-7")
                    ui.label(money_fmt_brl(report.expense_total)).classes("text-h6")

                with balance_card:
                    ui.label("Saldo").classes("text-grey-7")
                    ui.label(money_fmt_brl(report.balance)).classes("text-h6")

                ui.separator()

                by_cat = [
                    {
                        "category_name": c.category_name,
                        "planned": money_fmt_brl(c.planned),
                        "realized": money_fmt_brl(c.realized),
                        "deviation": money_fmt_brl(c.deviation),
                    }
                    for c in report.by_category
                ]

                with by_cat_table_container:
                    ui.label("Orçado vs Realizado (por categoria)").classes("text-subtitle1")

                    ui.table(
                        columns=[
                            {"name": "category_name", "label": "Categoria", "field": "category_name"},
                            {"name": "planned", "label": "Orçado", "field": "planned"},
                            {"name": "realized", "label": "Realizado", "field": "realized"},
                            {"name": "deviation", "label": "Desvio", "field": "deviation"},
                        ],
                        rows=by_cat,
                        row_key="category_name",
                    ).props("dense flat")

            async def on_refresh() -> None:
                refresh_btn.disable()
                try:
                    await render()
                finally:
                    refresh_btn.enable()

            with header_row:
                refresh_btn = ui.button("Atualizar", on_click=on_refresh).props("unelevated")

            # Render inicial
            await render()
