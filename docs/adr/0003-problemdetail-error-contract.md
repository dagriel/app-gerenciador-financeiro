# ADR 0003 — Contrato de erro padronizado (ProblemDetail + códigos estáveis)

**Status:** Accepted  
**Data:** 2026-01-15

## Contexto
APIs que não padronizam erros tendem a gerar:
- alto acoplamento do cliente (mobile/web) a mensagens “humanas” instáveis
- dificuldade de observabilidade (agrupar erros por tipo/código)
- inconsistência entre endpoints (cada rota responde diferente)

O FastAPI/Pydantic já fornece 422 estruturado, mas para erros de regra de negócio
(400/401/404/409) precisamos de um padrão consistente.

## Decisão
Adotar um contrato inspirado no RFC 7807 (**Problem Details**) com extensão:

- `status`, `title`, `detail`, `instance`
- `code` (código estável quando aplicável)
- `errors` (opcional; usado principalmente para 422 de validação)

### Códigos estáveis
Centralizar mensagens/códigos de erro no enum:
- `src/app/core/error_messages.py` (`ErrorMessage`)

E manter um catálogo humano para consumidores:
- `docs/ERROR_CATALOG.md`

### Fluxo de implementação
- Services levantam exceções de domínio (ex.: `BadRequestError`, `NotFoundError`, `ConflictError`)
  com `detail` baseado em `ErrorMessage` (ou string).
- Um handler global converte essas exceções em `ProblemDetail` para resposta HTTP.
- Erros de validação do Pydantic (422) também seguem um formato previsível, com `errors`.

## Consequências
### Positivas
- Contrato previsível para clientes (front/mobile)
- Melhor observabilidade (agrupar por `code`)
- Reduz duplicação de mensagens e “strings mágicas”
- Facilita documentação e QA

### Negativas / trade-offs
- `ErrorMessage` hoje está em `core` (cross-cutting). Se o domínio evoluir para Clean estrita,
  pode ser necessário mover/duplicar catálogo no domínio e mapear no boundary.

## Alternativas consideradas
1. Retornar mensagens livres por endpoint  
   Rejeitado: inconsistência e alto custo para clientes.
2. Usar apenas 422/HTTPException do FastAPI  
   Rejeitado: não cobre regras de negócio (409/400/404) de forma consistente.
3. Adotar uma lib externa completa de Problem Details  
   Rejeitado por enquanto: MVP prefere solução simples e explícita.

## Referências
- RFC 7807 — Problem Details for HTTP APIs
