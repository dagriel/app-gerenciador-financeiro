"""Domain error catalog (stable codes + user-facing messages).

This module is the "source of truth" for business error messages/codes.

Notes:
- Codes are stable and derived from the enum member name (e.g. TX_NOT_FOUND).
- Messages are user-facing (pt-BR) and can evolve carefully, but the code should remain stable.
"""

from __future__ import annotations

from enum import StrEnum


class ErrorMessage(StrEnum):
    # Auth
    API_KEY_INVALID = "API key inválida"

    # Categories
    CATEGORY_ALREADY_EXISTS = "Categoria já existe"
    CATEGORY_NOT_FOUND = "Categoria não encontrada"
    CATEGORY_INVALID_OR_INACTIVE = "Categoria inválida/inativa"

    # Accounts
    ACCOUNT_ALREADY_EXISTS = "Conta já existe"
    ACCOUNT_NOT_FOUND = "Conta não encontrada"
    ACCOUNT_INVALID_OR_INACTIVE = "Conta inválida/inativa"

    # Budgets
    BUDGET_ONLY_EXPENSE_MVP = "Orçamento só é suportado para categorias de despesa no MVP"
    BUDGET_NOT_FOUND = "Orçamento não encontrado"

    # Transactions
    TX_FROM_TO_BOTH_REQUIRED = "Informe from_date e to_date juntos"
    TX_USE_TRANSFER_ENDPOINT = "Use /transactions/transfer para transferências"
    TX_INCOME_REQUIRES_AMOUNT_GT_0 = "INCOME requer amount > 0"
    TX_EXPENSE_REQUIRES_AMOUNT_LT_0 = "EXPENSE requer amount < 0"
    TX_CATEGORY_ID_REQUIRED = "category_id é obrigatório para INCOME/EXPENSE"
    TX_CATEGORY_INCOMPATIBLE_INCOME = "Categoria incompatível com INCOME"
    TX_CATEGORY_INCOMPATIBLE_EXPENSE = "Categoria incompatível com EXPENSE"
    TX_NOT_FOUND = "Transação não encontrada"

    # Transfers (service)
    TRANSFER_SAME_ACCOUNTS = "Conta origem e destino não podem ser iguais."
    TRANSFER_AMOUNT_ABS_GT_0 = "amount_abs deve ser > 0"
    TRANSFER_FROM_ACCOUNT_INVALID = "Conta origem inválida/inativa"
    TRANSFER_TO_ACCOUNT_INVALID = "Conta destino inválida/inativa"

    # Month parsing/validation
    MONTH_FORMAT = "month deve estar no formato YYYY-MM"
    MONTH_RANGE = "month deve ter mês entre 01 e 12"
    MONTH_YEAR_RANGE = "month deve ter ano válido (1900..3000)"
