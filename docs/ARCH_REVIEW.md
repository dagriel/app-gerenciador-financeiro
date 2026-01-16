# Revisão de Arquitetura — APP-GERENCIADOR-FINANCEIRO

Este documento complementa o `docs/ARCHITECTURE.md` com uma **avaliação crítica**
(arquitetura atual vs melhores práticas), riscos e recomendações priorizadas.

> Escopo: MVP API-only (single-user local), FastAPI + SQLAlchemy + Alembic.

---

## 1) Resumo executivo

A base do projeto está bem alinhada com boas práticas modernas para APIs Python:

- **Controllers finos** (routers FastAPI) delegando para **services**.
- **Boundary transacional** por request com **Unit of Work**.
- **Repository Pattern** para centralizar queries.
- **Contrato de erro padronizado** (ProblemDetail + códigos estáveis).
- Evolução incremental para uma camada de **Domain** com regras puras.

Isso tende a escalar bem para evolução do MVP, com boa testabilidade e manutenibilidade.

---

## 2) Arquitetura atual (identificada)

### 2.1 Camadas / módulos
- **API**: `src/app/api/*`
  - Routers: `api/routers/*`
  - Dependências: `api/deps.py` (DI e boundary transacional via `get_uow`)
  - OpenAPI: `api/openapi.py`

- **Services (use-cases)**: `src/app/services/*`
  - Orquestram: regras + repos + flush.
  - Não fazem commit/rollback.

- **Domain**: `src/app/domain/*`
  - Value Objects/helpers: `domain/money.py`, `domain/validators.py`
  - Regras puras: `domain/rules/*`

- **Infra/Persistence**
  - SQLAlchemy models: `src/app/db/models.py`
  - Session: `src/app/db/session.py`
  - UoW: `src/app/db/uow.py`
  - Repositories: `src/app/repositories/*`

- **Core (cross-cutting)**: `src/app/core/*`
  - Config, logging, security
  - `ErrorMessage` (catálogo de erros) e exceções (`DomainError` e derivados)

### 2.2 Padrões presentes
- Unit of Work (request-scoped)
- Repository Pattern
- “Domain rules” (ainda pequeno, mas já estruturado)
- Problem Details (inspirado no RFC 7807)
- Money como Decimal

---

## 3) Pontos fortes (boas práticas aplicadas)

### 3.1 Boundary transacional correto
- `get_uow()` centraliza commit/rollback, evitando side effects nos services.
- Reduz bugs e melhora testabilidade.

### 3.2 Boa separação API vs negócio
- Routers “thin” -> Services.
- Erros do domínio sobem e são serializados no handler global.

### 3.3 Contrato de erro consistente
- `ErrorMessage` fornece **códigos estáveis**.
- `ProblemDetail` torna o consumo previsível (cliente/QA/observabilidade).

### 3.4 Estabilidade monetária
- `Decimal` + quantização e serializer garantem consistência de payload.

### 3.5 Qualidade automatizada
- Ruff + Pytest + Pyright no CI.
- Testes de “guardrail” arquitetural evitam drift.

---

## 4) Riscos / gaps vs arquitetura “ideal” (Clean/DDD) — com recomendação

### 4.1 Domain depende de Core (médio)
Hoje `domain/*` usa `ErrorMessage` e exceções definidas em `core`.
Isso é pragmático e bom para MVP, mas na Clean “pura” o domínio idealmente não
conhece detalhes da aplicação/infra.

**Recomendação (quando crescer):**
- Criar `domain/errors.py` com exceções puras (sem HTTP).
- Mapear exceções para HTTP em `main.py` (handler).
- Manter `ErrorMessage` como catálogo “shared” ou mover parte para `domain/catalog.py`.

### 4.2 Repositories em estilo `db.query` (baixo/médio)
Funciona, mas SQLAlchemy 2.0 recomenda `select()`/`session.execute()`.

**Recomendação:**
- Migração gradual (por arquivo ou por feature) para o estilo 2.0, sem pressa.

### 4.3 Domínio e entidade ORM são a mesma coisa (médio/alto se o domínio crescer)
Para MVP isso é ótimo (menos código). Porém, se o produto ganhar complexidade
(regras, integrações, importação de extrato, recorrências), separar pode fazer sentido.

**Recomendação:**
- Só separar quando houver ganho claro.
- Se separar:
  - Domain Entities (dataclasses/POPOs)
  - ORM models no infra
  - Mappers (infra <-> domain) nos repositories

### 4.4 Service layer com repetição de padrões (baixo)
Ex.: padrão de tratar `IntegrityError` para unicidade em accounts/categories.
Isso é aceitável, mas pode virar repetitivo.

**Recomendação:**
- Extrair helpers de aplicação (ex.: `app.services._db_errors`) para normalizar
  conversão de IntegrityError -> DomainError, se começar a se repetir muito.

---

## 5) Recomendações priorizadas (backlog)

### Prioridade A (alto impacto / baixo risco)
1. Expandir testes unitários para `domain/rules/*` (cobertura e evolução segura)
2. Manter routers “thin” e sem `Session`/SQLAlchemy direto (já garantido por guardrails)
3. Documentar novas decisões arquiteturais com ADRs conforme o projeto evoluir

### Prioridade B (médio prazo)
4. Isolar Domain de Core (exceções e catálogo) se o projeto crescer
5. Migrar repositórios para SQLAlchemy 2.0 style

### Prioridade C (futuro)
6. Separar Domain Entities de ORM Entities (se e quando necessário)
7. Observabilidade: correlation-id, tracing e métricas

---

## 6) Evidências (status atual)
- `docs/ARCHITECTURE.md`: arquitetura e guidelines
- `tests/test_architecture.py`: guardrails automatizados
- CI (`.github/workflows/ci.yml`) roda ruff/format/pyright/pytest
