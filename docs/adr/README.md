# ADRs (Architecture Decision Records)

Este diretório guarda **decisões arquiteturais** relevantes do projeto, no formato ADR.

## Por que ADR?
- Preserva o “porquê” das escolhas (trade-offs)
- Evita retrabalho e discussões recorrentes
- Ajuda novos contribuidores a entenderem o desenho

## Quando criar um ADR?
Crie um ADR quando houver uma decisão que:
- muda dependências entre camadas
- altera contrato (API, erros, regras)
- introduz novo padrão (ex.: UoW, Repository, Domain rules)
- altera estratégia de persistência (SQLite → Postgres, etc.)

## Formato sugerido
Nome do arquivo: `NNNN-titulo-kebab-case.md`

Seções recomendadas:
- Contexto
- Decisão
- Consequências
- Alternativas consideradas
- Links/Referências

## Status
Use um dos status:
- **Proposed**
- **Accepted**
- **Deprecated**
- **Superseded** (referenciar novo ADR)
