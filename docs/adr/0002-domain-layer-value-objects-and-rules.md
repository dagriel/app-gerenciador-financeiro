# ADR 0002 — Introdução de camada Domain (Value Objects + regras puras) com compatibilidade

**Status:** Accepted  
**Data:** 2026-01-15

## Contexto
O projeto começou como um MVP com regras de negócio concentradas em `services/*`
e alguns helpers em `core/*`. Conforme o domínio cresceu (money/meses/regras de
transação/orçamento), surgiram necessidades:

- Centralizar invariantes e validações para reduzir duplicação
- Tornar regras facilmente testáveis **sem DB** e sem FastAPI
- Permitir evolução gradual sem refatoração grande (evitar quebrar imports existentes)

## Decisão
Criamos uma camada **Domain** para regras puras e Value Objects:

- `src/app/domain/money.py`: helpers de dinheiro (Decimal/quantize/serialize)
- `src/app/domain/validators.py`: parsing/validação de mês (YYYY-MM)
- `src/app/domain/rules/*`: regras puras (sem I/O) por subdomínio (ex.: transactions, budgets)

### Compatibilidade (migração incremental)
Para evitar quebra de imports existentes:
- `src/app/core/money.py` virou um **módulo compat** que reexporta `app.domain.money`
- `src/app/core/validators.py` virou um **módulo compat** que reexporta `app.domain.validators`

### Uso pelos services
Os services passam a delegar invariantes para o domínio:
- `services/transactions.py` → `domain/rules/transactions.py`
- `services/transfers.py` → `domain/rules/transactions.py`
- `services/budgets.py` → `domain/rules/budgets.py`

## Consequências
### Positivas
- Regras ficam **reutilizáveis** e centralizadas (menos duplicação)
- Regras mais testáveis (sem DB / sem HTTP)
- Refatoração incremental (reexports mantêm código legível e estável)
- Facilita evolução futura (ex.: separar domain errors, entities, etc.)

### Negativas / trade-offs
- Por pragmatismo, o Domain ainda depende de `core` para `ErrorMessage`/exceções
  (contrato de erro estável). Em Clean estrita, isso seria invertido.

## Alternativas consideradas
1. Manter regras em services  
   Rejeitado: duplicação e baixa reutilização.
2. Refatorar tudo “big bang”  
   Rejeitado: alto risco e alto custo para MVP.
3. Domain “puro” sem depender de core desde já  
   Possível, mas adicionaria complexidade antecipada; decidido postergar.

## Referências
- Clean Architecture / Onion Architecture (separação por dependências)
- DDD tático (Value Objects e invariantes no domínio)
