# ADR 0005 — Guardrails de arquitetura via testes (anti-drift)

**Status:** Accepted  
**Data:** 2026-01-15

## Contexto
Com o crescimento do projeto, é comum a arquitetura “degradar” (drift), por exemplo:

- Routers começam a fazer SQL diretamente
- Services passam a importar FastAPI/HTTP concerns
- Domain passa a depender de SQLAlchemy/DB
- Commits/rollbacks se espalham fora do boundary transacional

Esses problemas são difíceis de detectar cedo somente via revisão de PR, e custam caro
quando se tornam “padrão” no codebase.

## Decisão
Adicionar **testes automatizados** que impõem regras de dependência entre camadas e
regras básicas de boundary transacional.

Implementação:
- `tests/test_architecture.py`
  - `test_layer_dependencies`: valida imports permitidos/proibidos por camada
    - Domain não importa FastAPI/SQLAlchemy/db/services/repos
    - Services não importam FastAPI/HTTP layer
    - Routers não importam `app.db.session` e não acessam repositories diretamente
  - `test_no_commit_or_rollback_outside_boundary`: proíbe `.commit(` e `.rollback(` em
    `services/` e `repositories/` (boundary fica no `get_uow()`)

Rodar localmente:
- `pytest -k architecture`

## Consequências
### Positivas
- Evita drift arquitetural de forma contínua
- “Falha rápido” em PRs que violam boundaries
- Complementa revisão humana (não substitui)

### Negativas / trade-offs
- Regras precisam ser pragmáticas (para não virar “burocracia”)
- Pode gerar falsos positivos se a regra for muito ampla
- Exige manutenção quando a arquitetura evoluir

## Alternativas consideradas
1. Só revisão de PR  
   Rejeitado: detecta tarde e depende do revisor lembrar de todas as regras.
2. Adotar ferramentas externas de arquitetura (ex.: imports graph/lint específico)  
   Possível, mas testes em Python puro são simples, explícitos e portáveis no MVP.

## Referências
- Clean Architecture: dependências apontando para dentro
- Prática comum em projetos grandes: “architecture tests” (guardrails)
