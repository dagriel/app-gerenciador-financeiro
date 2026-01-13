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

### 4. Execute a aplicação

```powershell
uvicorn app.main:app --reload
```

A API estará disponível em: **http://127.0.0.1:8000**

## 📖 Documentação da API

Acesse a documentação interativa (Swagger UI):

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔐 Autenticação

Todas as requisições (exceto `/health`) exigem o header **X-API-Key**:

```bash
curl -H "X-API-Key: CHANGE_ME_LOCAL" http://127.0.0.1:8000/health
```

Para desabilitar a proteção (apenas desenvolvimento):

```env
API_KEY_ENABLED=false
```

## 💡 Exemplos de Uso

### Observação importante (valores monetários)

Para evitar problemas de precisão de `float`, este MVP usa contrato “clean”:

- A API **retorna** valores monetários como **string** (ex.: `"5000.00"`, `"-150.50"`).
- A API **aceita** valores monetários como **string** (recomendado) ou número, mas a normalização final sempre será em 2 casas decimais.


### Health Check

```bash
curl -H "X-API-Key: CHANGE_ME_LOCAL" http://127.0.0.1:8000/health
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
