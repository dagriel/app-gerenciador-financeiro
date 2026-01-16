# Catálogo de Erros (ProblemDetail)

Este documento descreve **todos os códigos de erro (`code`)** retornados pela API no formato **ProblemDetail**.

## Formato padrão (ProblemDetail)

A API padroniza erros no payload:

```json
{
  "status": 400,
  "title": "Bad Request",
  "detail": "Mensagem legível",
  "code": "ERROR_CODE_OPCIONAL",
  "instance": "/rota",
  "errors": []
}
```

Notas importantes:

- `code`:
  - Quando o erro vem de uma regra do domínio (ex.: `ErrorMessage`), o `code` é o **nome estável** do enum (ex.: `ACCOUNT_NOT_FOUND`).
  - Para erros do roteamento do framework (ex.: 404 rota inexistente, 405 method not allowed), o `code` normalmente **não existe**.
- `errors`: **opcional**, usado principalmente em **422** (validação do Pydantic). Em geral **não** aparece em 400/401/404/409/405.

---

## Códigos globais (framework/validação)

| code | status | Quando ocorre | Observações |
|------|--------|---------------|-------------|
| `REQUEST_VALIDATION_ERROR` | 422 | Erro de validação do Pydantic (body/query/path) | `errors` vem preenchido com a lista de falhas |

### Exemplos (sem `code`)

| status | Cenário | Observação |
|--------|---------|-----------|
| 404 | Rota inexistente (ex.: `/accounts_FAKE`) | `detail` tende a ser `"Not Found"` |
| 405 | Método não permitido (ex.: `POST /accounts/1`) | `detail` tende a ser `"Method Not Allowed"` |

---

## Autenticação

| code | status | Quando ocorre |
|------|--------|---------------|
| `API_KEY_INVALID` | 401 | Header `X-API-Key` ausente ou inválido (quando `API_KEY_ENABLED=true`) |

---

## Accounts (Contas)

| code | status | Quando ocorre |
|------|--------|---------------|
| `ACCOUNT_ALREADY_EXISTS` | 409 | Criar/renomear conta para um `name` já existente (mesmo tipo) |
| `ACCOUNT_NOT_FOUND` | 404 | Atualizar/deletar conta inexistente |
| `ACCOUNT_INVALID_OR_INACTIVE` | 400 | Conta inexistente ou `active=false` usada em transações |

---

## Categories (Categorias)

| code | status | Quando ocorre |
|------|--------|---------------|
| `CATEGORY_ALREADY_EXISTS` | 409 | Criar/renomear categoria para um `name` já existente |
| `CATEGORY_NOT_FOUND` | 404 | Atualizar/deletar categoria inexistente |
| `CATEGORY_INVALID_OR_INACTIVE` | 400 | Categoria inexistente ou `active=false` usada em transações/orçamentos |

---

## Budgets (Orçamentos)

| code | status | Quando ocorre |
|------|--------|---------------|
| `BUDGET_ONLY_EXPENSE_MVP` | 400 | Tentar criar orçamento para categoria `INCOME` |
| `BUDGET_NOT_FOUND` | 404 | Deletar orçamento inexistente |
| `MONTH_FORMAT` | 400 | `month` inválido em query string (não segue `YYYY-MM`) |
| `MONTH_RANGE` | 400 | `month` com mês fora de `01..12` em query string |
| `MONTH_YEAR_RANGE` | 400 | `month` com ano fora de `1900..3000` em query string |

> Nota: no **body** do `POST /budgets`, `month` é validado pelo schema e pode resultar em **422** (`REQUEST_VALIDATION_ERROR`) quando inválido.

---

## Transactions (Transações)

| code | status | Quando ocorre |
|------|--------|---------------|
| `TX_FROM_TO_BOTH_REQUIRED` | 400 | `from_date` sem `to_date` (ou vice-versa) |
| `TX_USE_TRANSFER_ENDPOINT` | 400 | Enviar `kind=TRANSFER` em `POST /transactions` |
| `TX_INCOME_REQUIRES_AMOUNT_GT_0` | 400 | `kind=INCOME` com `amount <= 0` |
| `TX_EXPENSE_REQUIRES_AMOUNT_LT_0` | 400 | `kind=EXPENSE` com `amount >= 0` |
| `TX_CATEGORY_ID_REQUIRED` | 400 | `category_id` ausente em INCOME/EXPENSE |
| `TX_CATEGORY_INCOMPATIBLE_INCOME` | 400 | Categoria `EXPENSE` usada com `kind=INCOME` |
| `TX_CATEGORY_INCOMPATIBLE_EXPENSE` | 400 | Categoria `INCOME` usada com `kind=EXPENSE` |
| `TX_NOT_FOUND` | 404 | Deletar transação inexistente |

---

## Transfers (Transferências)

| code | status | Quando ocorre |
|------|--------|---------------|
| `TRANSFER_SAME_ACCOUNTS` | 400 | `from_account_id == to_account_id` |
| `TRANSFER_AMOUNT_ABS_GT_0` | 400 | `amount_abs <= 0` |
| `TRANSFER_FROM_ACCOUNT_INVALID` | 400 | Conta origem inexistente/inativa |
| `TRANSFER_TO_ACCOUNT_INVALID` | 400 | Conta destino inexistente/inativa |

---

## Month parsing/validation (utilizado por budgets/reports)

| code | status | Quando ocorre |
|------|--------|---------------|
| `MONTH_FORMAT` | 400 | `month` inválido (não `YYYY-MM`) |
| `MONTH_RANGE` | 400 | mês fora de `01..12` |
| `MONTH_YEAR_RANGE` | 400 | ano fora de `1900..3000` |
