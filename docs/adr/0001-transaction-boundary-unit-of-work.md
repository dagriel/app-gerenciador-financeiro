# ADR 0001 — Boundary transacional via Unit of Work (UoW)

**Status:** Accepted  
**Data:** 2026-01-15

## Contexto
O projeto é um MVP API-only com FastAPI + SQLAlchemy. Precisamos de um padrão
consistente para controlar transações e evitar:

- commits espalhados em services/repositories
- inconsistência entre endpoints e scripts
- dificuldades de teste (principalmente em cenários de erro)

## Decisão
Adotamos o padrão **Unit of Work** por request (boundary transacional):

- A dependência FastAPI `get_uow()` cria a sessão, instancia `UnitOfWork` e
  controla `commit()`/`rollback()`.
- **Services** recebem `UnitOfWork` e usam `uow.session` para operações de banco.
- Services podem chamar `uow.flush()` quando precisarem de PK antes do commit final.
- Repositories recebem `Session` e **não** fazem commit/rollback.

Implementação:
- `src/app/api/deps.py`: `get_uow()`
- `src/app/db/uow.py`: wrapper mínimo (session/flush)

## Consequências
### Positivas
- Transações consistentes por request
- Melhor testabilidade e previsibilidade (um único ponto de commit)
- Services mais “puros” (sem side effects transacionais)

### Negativas / trade-offs
- A camada de API (deps) precisa conhecer `db.session`
- Para cenários avançados (nested transactions, outbox), o UoW terá que evoluir

## Alternativas consideradas
1. Services controlarem commit/rollback  
   Rejeitado: espalha responsabilidade e dificulta rollback consistente.
2. Usar autocommit / sem transação explícita  
   Rejeitado: aumenta risco de estados intermediários e inconsistência.
3. Transação no middleware (sem UoW)  
   Possível, mas o UoW dá uma interface explícita e testável para `flush()`.

## Referências
- Martin Fowler — Unit of Work
- SQLAlchemy Sessions/Transactions
