## O que mudou
<!-- Descreva as principais mudanças deste PR -->

## Como testar
<!-- Passo a passo para testar as mudanças -->

## Evidências
<!-- Screenshots, logs, exemplos de payloads testados, etc. -->

## DoD (Definition of Done - verificar 03 vezes)

### ✅ Verificação 1 - Autor (antes do PR)
- [ ] `ruff check .` sem erros
- [ ] `ruff format .` aplicado
- [ ] `pytest` passando localmente
- [ ] **Regras de domínio validadas**: sinais corretos (receita +, despesa -), transferência gera 2 transações, orçamento único por mês/categoria

### ✅ Verificação 2 - Revisor (peer review)
- [ ] Lógica atende os critérios de aceite da história/feature
- [ ] Não aumentou complexidade desnecessária
- [ ] Logs e tratamento de erro adequados
- [ ] Segurança básica: validação de input (Pydantic), sem dados sensíveis em logs
- [ ] **Dinheiro com Decimal**: conversão correta de `float -> Decimal(str(x))` onde necessário

### ✅ Verificação 3 - CI (gates automáticos)
- [ ] **ruff check + format** passando
- [ ] **pytest + coverage** passando
- [ ] **CodeQL** sem alertas críticos

### 📋 Qualidade de Código e Design
- [ ] **Clean Code**: código limpo, sem duplicações óbvias
- [ ] **Refatoração**: regras de negócio em `services/`, não espalhadas em routers
- [ ] **Documentação Inline**: comentários explicam o **porquê** (decisões), não o **como**

### 🧪 Testes e Validação
- [ ] Testes unitários/integração cobrindo as mudanças
- [ ] Critérios de aceite validados (listados em "Como testar")

### 🔒 Segurança e Compliance
- [ ] Input validado via Pydantic schemas
- [ ] Sem dados sensíveis em logs (API keys, senhas, tokens)
- [ ] Queries filtradas adequadamente (evitar vazamento entre contextos)

### 📊 Infraestrutura e Observabilidade
- [ ] Logs estruturados mantidos/ajustados em operações críticas
- [ ] Tratamento de erro com mensagens claras

### 📚 Documentação e Conhecimento
- [ ] **README** atualizado (se mudou setup, env vars, comandos)
- [ ] **OpenAPI/Swagger** atualizado (automático no FastAPI, mas validar contratos)
- [ ] Se mudou modelos: **migração Alembic criada** e testada em DB limpo

---

## Checklist de Contexto (se aplicável)

### Para mudanças em modelos/schemas:
- [ ] Migração Alembic criada: `alembic revision --autogenerate -m "descrição"`
- [ ] Migração testada: `alembic upgrade head` em DB limpo
- [ ] Schemas Pydantic atualizados e coerentes com modelos

### Para mudanças em transações/transferências:
- [ ] Validação de sinais (receita +, despesa -)
- [ ] Transferência cria/deleta par corretamente
- [ ] Testes cobrem edge cases (contas iguais, valores zero/negativos)

### Para mudanças em relatórios:
- [ ] Filtros de data tipados como `datetime.date`
- [ ] Agregações usam Decimal internamente
- [ ] Categorias inativas não quebram relatório (se aplicável)
