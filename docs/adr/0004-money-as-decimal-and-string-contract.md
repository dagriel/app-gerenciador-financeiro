# ADR 0004 — Dinheiro como Decimal + contrato de API em string

**Status:** Accepted  
**Data:** 2026-01-15

## Contexto
Valores monetários em `float` geram problemas clássicos de precisão (ex.: 0.1 + 0.2).
Além disso, clientes (front/mobile) tendem a sofrer com inconsistências quando o
backend retorna `number` com arredondamentos diferentes.

Como é um app financeiro, consistência e previsibilidade são essenciais.

## Decisão
1. Internamente, dinheiro é tratado como **Decimal**.
2. A API **retorna** dinheiro como **string** com 2 casas (ex.: `"5000.00"`, `"-150.50"`).
3. A API **aceita** dinheiro como string (recomendado) ou número, mas converte com segurança.

Implementação:
- `src/app/domain/money.py`: `to_decimal`, `quantize_money`, `serialize_money`
- `src/app/schemas/types.py`: tipo Pydantic que valida e normaliza para Decimal
- `src/app/core/money.py`: reexport (compatibilidade)

## Consequências
### Positivas
- Precisão consistente (evita bugs de float)
- Contrato previsível para clientes
- Facilita testes e relatórios (agregações com Decimal)

### Negativas / trade-offs
- Clientes precisam lidar com string (mas isso é comum/aceito em APIs financeiras)
- Necessita disciplina: nunca usar `float` em regras/cálculos

## Alternativas consideradas
1. Usar float com arredondamento em todo lugar  
   Rejeitado: é fonte de bugs e divergências.
2. Retornar number e aceitar number sempre  
   Rejeitado: risco de precisão/representação em JSON + linguagens.

## Referências
- Problemas de ponto flutuante em finanças (IEEE 754)
- Boas práticas de APIs financeiras (money-as-string)
