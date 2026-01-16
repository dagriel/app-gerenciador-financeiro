# APP-GERENCIADOR-FINANCEIRO

MVP de API para controle financeiro pessoal (single-user local) com FastAPI + SQLAlchemy + Alembic.

## 🎯 Características

- ✅ **API-only** (sem interface web no MVP)
- ✅ **Single-user local** (sem multi-tenancy)
- ✅ **SQLite** (banco de dados local)
- ✅ **Gestão de contas e categorias**
- ✅ **Transações** (receitas, despesas, transferências)
- ✅ **Orçamento mensal** por categoria
- ✅ **Relatórios** mensais (orçado vs realizado)
- ✅ **API Key** para proteção básica
- ✅ **Logs estruturados** (JSON)
- ✅ **Testes automatizados** (pytest)
- ✅ **CI/CD** (GitHub Actions)

## 📋 Requisitos

- **Python 3.13+**
- **pip** (gerenciador de pacotes)
- **SQLite** (incluído no Python)

## 🚀 Setup

### 1. Clone e ative o ambiente virtual

```powershell
# Clone o repositório
git clone <url-do-repo>
cd app-gerenciador-financeiro

# Crie e ative o ambiente virtual (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instale as dependências
pip install -e ".[dev]"
```

### 2. Configure o ambiente

```powershell
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o .env e ajuste a API_KEY
notepad .env
```

Variáveis disponíveis no `.env`:

```env
DATABASE_URL=sqlite:///./app.db
API_KEY_ENABLED=true
API_KEY=CHANGE_ME_LOCAL
LOG_LEVEL=INFO
```

### 3. Inicialize o banco de dados

> ✅ **As migrações do Alembic já estão versionadas no repositório** (pasta `alembic/`).
> Para iniciar o banco local, basta aplicar as migrações:

```powershell
alembic upgrade head
```

> Se você alterar os modelos e precisar gerar uma nova migração:
>
> ```powershell
> alembic revision --autogenerate -m "descricao da alteracao"
> alembic upgrade head
> ```
>
> ⚠️ **SQLite + Alembic (importante)**  
> O SQLite não suporta `ALTER TABLE ... ADD CONSTRAINT`. Se a migração envolver **constraints**
> (ex.: UNIQUE) ou outras alterações estruturais que o SQLite não suporta via `ALTER`,
> use o **batch mode** do Alembic (estratégia *copy-and-move*):
>
> ```py
> from alembic import op
>
> with op.batch_alter_table("accounts", schema=None) as batch_op:
>     batch_op.create_unique_constraint("uq_account_name_type", ["name", "type"])
> ```

### 4. Seeds (dados iniciais do MVP)

Este projeto inclui um **seed idempotente** para acelerar validação do MVP, demos e QA.

> Recomendado (dataset determinístico completo, incluindo transações e 1 transferência):
```powershell
python -m app.db.seed --reset --month 2026-01 --with-sample-transactions
```

- `--reset`: apaga dados das tabelas do domínio (transactions/budgets/categories/accounts) e recria tudo do zero.
- Sem `--reset`: executa em modo **upsert** (não duplica contas/categorias/orçamentos).  
  Para evitar duplicação silenciosa, as transações são **puladas** se o DB já tiver transações.

> Somente estrutura mínima (contas/categorias/orçamentos, sem transações):
```powershell
python -m app.db.seed --reset --month 2026-01
```

### 5. Execute a aplicação

```powershell
uvicorn app.main:app --reload
```

A API estará disponível em: **http://127.0.0.1:8000**

## 📖 Documentação da API

Acesse a documentação interativa (Swagger UI):

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔐 Autenticação

Todas as requisições **(exceto `/health`)** exigem o header **X-API-Key**.

Exemplo (listar contas):

```bash
curl -H "X-API-Key: CHANGE_ME_LOCAL" http://127.0.0.1:8000/accounts
```

Para desabilitar a proteção (apenas desenvolvimento):

```env
API_KEY_ENABLED=false
```

## 🧾 Contrato de erros (ProblemDetail)

Este MVP padroniza as respostas de erro no formato **ProblemDetail** (inspirado no RFC 7807).

> 📌 **Catálogo oficial de códigos/erros**: veja [`docs/ERROR_CATALOG.md`](docs/ERROR_CATALOG.md)

Formato:

```json
{
  "status": 400,
  "title": "Bad Request",
  "detail": "Mensagem legível",
  "code": "ERROR_CODE_OPCIONAL",
  "instance": "/rota"
}
```

Campos:

- `detail`: mensagem humana (pt-BR)
- `code`: **código estável** (quando aplicável), derivado dos enums internos (ex.: `TX_NOT_FOUND`, `API_KEY_INVALID`)
- `instance`: path da requisição
- `errors`: **opcional**, presente principalmente em **422** (erros de validação do Pydantic)

### 400 vs 422 (importante)

- **422 Unprocessable Entity**: erro de validação do **Pydantic** (schema). Ex.: campo obrigatório ausente, tipo inválido, `amount_abs <= 0`, etc.
- **400 Bad Request**: validação de **regra de negócio** ou validação manual em query params. Ex.: filtro `from_date/to_date`, mês inválido em query string (`month`), categoria/conta inválida/inativa, etc.

### Exemplos reais

**401 Unauthorized** (API key inválida ou ausente quando habilitada):

```json
{
  "status": 401,
  "title": "Unauthorized",
  "detail": "API key inválida",
  "code": "API_KEY_INVALID",
  "instance": "/accounts"
}
```

**404 Not Found** (rota inexistente; retorno de roteamento do framework):

```json
{
  "status": 404,
  "title": "Not Found",
  "detail": "Not Found",
  "instance": "/accounts_FAKE"
}
```

**405 Method Not Allowed** (método não permitido; retorno de roteamento do framework):

```json
{
  "status": 405,
  "title": "Method Not Allowed",
  "detail": "Method Not Allowed",
  "instance": "/accounts"
}
```

**422 Unprocessable Entity** (validação; com `errors`):

```json
{
  "status": 422,
  "title": "Unprocessable Entity",
  "detail": "Erro de validação",
  "code": "REQUEST_VALIDATION_ERROR",
  "instance": "/transactions/transfer",
  "errors": [
    {
      "loc": ["body", "amount_abs"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

> Observação: por padrão, o Swagger/OpenAPI descreve apenas operações existentes.  
> Para melhorar a fidelidade do contrato, este projeto documenta como respostas “comuns” os erros que de fato podem ocorrer de forma transversal (**401/405/422**).  
> Já o **404** é documentado principalmente em rotas com **path params** (ex.: `/accounts/{account_id}`) para representar **resource not found**; o 404 por “rota inexistente” é um comportamento do roteamento do framework (não específico de uma operação).

## 💡 Exemplos de Uso

### Observação importante (valores monetários)

Para evitar problemas de precisão de `float`, este MVP usa contrato “clean”:

- A API **retorna** valores monetários como **string** (ex.: `"5000.00"`, `"-150.50"`).
- A API **aceita** valores monetários como **string** (recomendado) ou número, mas a normalização final sempre será em 2 casas decimais.


### Health Check

`/health` não requer autenticação:

```bash
curl http://127.0.0.1:8000/health
```

### Criar Conta

```bash
curl -X POST http://127.0.0.1:8000/accounts \
  -H "X-API-Key: CHANGE_ME_LOCAL" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Banco\",\"type\":\"BANK\"}"
```

### Criar Categoria

```bash
curl -X POST http://127.0.0.1:8000/categories \
  -H "X-API-Key: CHANGE_ME_LOCAL" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alimentação\",\"kind\":\"EXPENSE\",\"group\":\"ESSENTIAL\"}"
```

### Criar Despesa

```bash
curl -X POST http://127.0.0.1:8000/transactions \
  -H "X-API-Key: CHANGE_ME_LOCAL" \
  -H "Content-Type: application/json" \
  -d "{\"date\":\"2026-01-15\",\"description\":\"Supermercado\",\"amount\":\"-150.50\",\"kind\":\"EXPENSE\",\"account_id\":1,\"category_id\":1}"
```

### Criar Transferência

```bash
curl -X POST http://127.0.0.1:8000/transactions/transfer \
  -H "X-API-Key: CHANGE_ME_LOCAL" \
  -H "Content-Type: application/json" \
  -d "{\"date\":\"2026-01-20\",\"description\":\"Movimentação\",\"amount_abs\":\"100.00\",\"from_account_id\":1,\"to_account_id\":2}"
```

### Criar Orçamento

```bash
curl -X POST http://127.0.0.1:8000/budgets \
  -H "X-API-Key: CHANGE_ME_LOCAL" \
  -H "Content-Type: application/json" \
  -d "{\"month\":\"2026-01\",\"category_id\":1,\"amount_planned\":\"500.00\"}"
```

### Relatório Mensal

```bash
curl -H "X-API-Key: CHANGE_ME_LOCAL" \
  "http://127.0.0.1:8000/reports/monthly-summary?month=2026-01"
```

## 🗄️ Visualizar Banco de Dados

Para explorar o banco de dados SQLite usando o DBeaver ou outras ferramentas, consulte o guia completo:

📘 **[Guia de Configuração do DBeaver](docs/DBEAVER_SETUP.md)**

O guia inclui:
- Passo a passo para conectar ao banco no DBeaver
- Estrutura detalhada de todas as tabelas
- Queries SQL úteis para análise de dados
- Alternativas ao DBeaver (SQLite Browser, VSCode Extensions)
- Considerações importantes sobre concorrência

## 🧪 Testes

### Executar todos os testes

```powershell
pytest
```

### Executar com cobertura

```powershell
pytest --cov=src --cov-report=term-missing
```

### Executar testes específicos

```powershell
pytest tests/test_transfers.py
pytest tests/test_budgets_reports.py -v
```

## 🛠️ Qualidade de Código

### Lint

```powershell
ruff check .
```

### Format

```powershell
ruff format .
```

### Type check (opcional)

```powershell
pyright
```

### Verificação completa (antes de commit)

```powershell
ruff check . && ruff format . && pytest
```

## 📊 Estrutura do Projeto

```
app-gerenciador-financeiro/
├── src/app/              # Código da aplicação
│   ├── api/              # Routers e dependências da API
│   ├── core/             # Config, logging, segurança
│   ├── db/               # Modelos ORM, sessão, migrations
│   ├── schemas/          # Schemas Pydantic
│   └── services/         # Regras de negócio
├── tests/                # Testes automatizados
├── alembic/              # Migrations do banco de dados
├── .env.example          # Exemplo de variáveis de ambiente
├── pyproject.toml        # Dependências e configurações
└── README.md             # Este arquivo
```

## 🏛️ Arquitetura (padrões do projeto)

Leitura recomendada:
- **Arquitetura e guidelines**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Revisão crítica (gaps + recomendações)**: [`docs/ARCH_REVIEW.md`](docs/ARCH_REVIEW.md)
- **Decisões arquiteturais (ADRs)**: [`docs/adr/README.md`](docs/adr/README.md)

Este projeto segue uma arquitetura em camadas com foco em manutenibilidade e testabilidade:

- **Routers (API)**: devem ser *thin* (apenas I/O HTTP + delegação)
- **Services (use-cases)**: orquestração do caso de uso; **não** fazem commit/rollback
- **Domain**: regras/invariantes e Value Objects (sem I/O)
- **Repositories**: centralizam **queries** reutilizáveis e/ou complexas
- **Unit of Work (UoW)**: boundary transacional por request/script (commit/rollback controlado fora do service)

Regras práticas:
- Routers injetam `UnitOfWork` via `Depends(get_uow)`
- Services recebem `UnitOfWork` e usam `uow.session` + `uow.flush()`
- Repositories recebem `Session` e **não** realizam commit
- Regras puras ficam em `src/app/domain/*` (ex.: `domain/rules/*`)
- “Guardrails” automatizados de arquitetura: `pytest -k architecture` (evita drift entre camadas)

## 🔄 Workflow de Desenvolvimento

1. **Criar branch** para a feature/fix
2. **Desenvolver** e testar localmente
3. **Executar qualidade**: `ruff check . && ruff format . && pytest`
4. **Commit** com mensagem descritiva
5. **Push** e abrir **Pull Request**
6. **CI passa** (lint + tests + SAST)
7. **Merge** após aprovação

## 📝 Regras de Domínio

### Transações

- **Receita** (`INCOME`): `amount > 0`
- **Despesa** (`EXPENSE`): `amount < 0`
- **Transferência** (`TRANSFER`): gera **2 transações** ligadas por `transfer_pair_id`
  - Saída (negativa) na conta origem
  - Entrada (positiva) na conta destino

### Orçamento

- Somente para categorias de **despesa** (`EXPENSE`)
- Único por `(mês, categoria)`
- `amount_planned` deve ser **positivo**

### Exclusão

- **Contas/Categorias**: soft delete (`active=false`)
  - Por padrão, `GET /accounts` e `GET /categories` retornam **apenas ativos**
  - Use `?include_inactive=true` para incluir registros inativos
- **Transferência**: deletar uma transação **remove o par completo**

## 🚨 Troubleshooting

### Erro: "Could not find platform independent libraries"

Se você estiver usando Python 3.13 e encontrar esse aviso, verifique:

```powershell
where python
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

Esse aviso costuma ser apenas um *warning* do ambiente. O projeto foi testado em **Python 3.13**.
Se você optar por usar **Python 3.12.x**, ajuste o `requires-python` no `pyproject.toml`.

### Erro: "database is locked"

O SQLite tem limitações de concorrência. Para produção, migre para PostgreSQL:

```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Testes falhando por cache de engine

O `conftest.py` já limpa o cache. Se persistir, delete:

```powershell
Remove-Item -Recurse -Force .pytest_cache
```

## 📦 CI/CD

O projeto usa GitHub Actions para:

- ✅ **Lint** (ruff)
- ✅ **Tests** (pytest + coverage)
- ✅ **SAST** (CodeQL)

Configuração em: `.github/workflows/ci.yml` e `.github/workflows/codeql.yml`

## 🎯 Roadmap

### MVP (atual) ✅
- Contas, categorias, transações
- Transferências
- Orçamento mensal
- Relatórios básicos

### V1 (próximos passos)
- [ ] Recorrências automáticas
- [ ] Exportação de dados (CSV/JSON)
- [ ] Dashboards avançados
- [ ] Filtros e paginação

### V2 (futuro)
- [ ] Categorização inteligente
- [ ] Anexos/comprovantes
- [ ] Metas financeiras
- [ ] Multi-moeda

## 📄 Licença

Este projeto é de uso pessoal e educacional.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com FastAPI + SQLAlchemy + Alembic** 🚀
