from __future__ import annotations

from pydantic import BaseModel, ConfigDict


MoneyStr = str


class MonthlySummaryByCategoryOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    category_id: int
    category_name: str
    planned: MoneyStr
    realized: MoneyStr
    deviation: MoneyStr


class MonthlySummaryOut(BaseModel):
    """Contrato do relatório mensal consumido pela UI.

    Observações (alinhadas ao backend):
    - expense_total vem como valor absoluto (positivo).
    - deviation = realized - planned (pode ser negativo).
    - valores monetários trafegam como string com 2 casas decimais.
    """

    model_config = ConfigDict(extra="ignore")

    month: str
    income_total: MoneyStr
    expense_total: MoneyStr
    balance: MoneyStr
    by_category: list[MonthlySummaryByCategoryOut]
