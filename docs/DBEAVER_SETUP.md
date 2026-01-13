# 🗄️ Como Abrir o Banco de Dados no DBeaver

Este guia explica como conectar e visualizar o banco de dados SQLite da aplicação usando o DBeaver.

## 📋 Pré-requisitos

1. **DBeaver Community** instalado (download em: https://dbeaver.io/download/)
2. **Banco de dados criado**: Execute a aplicação pelo menos uma vez para gerar o arquivo `app.db`

```powershell
# Certifique-se de que o banco foi criado
alembic upgrade head
```

## 🔧 Configuração da Conexão no DBeaver

### Passo 1: Abrir DBeaver e Criar Nova Conexão

1. Abra o **DBeaver**
2. Clique em **Database** → **New Database Connection** (ou pressione `Ctrl+N`)
3. Na janela de seleção, procure por **SQLite** e selecione
4. Clique em **Next**

### Passo 2: Configurar Caminho do Banco

Na aba **Main**:

1. **Path**: Clique em **Browse** e navegue até o arquivo do banco de dados:
   ```
   C:\Users\dalacruz\Downloads\projetos\study\app-gerenciador-financeiro\app.db
   ```
   
2. **Connection name** (opcional): Coloque um nome descritivo, por exemplo:
   ```
   Gerenciador Financeiro - Local
   ```

3. Clique em **Test Connection** para verificar se está funcionando
   - Se for a primeira vez, o DBeaver pode solicitar o download do driver SQLite
   - Clique em **Download** e aguarde a conclusão

4. Clique em **Finish**

### Passo 3: Explorar o Banco de Dados

Após conectar, você verá na árvore de navegação:

```
📁 Gerenciador Financeiro - Local
  └─ 📁 Databases
      └─ 📁 main
          ├─ 📋 Tables
          │   ├─ accounts       (Contas bancárias/carteiras)
          │   ├─ alembic_version (Controle de migrações)
          │   ├─ budgets        (Orçamentos mensais)
          │   ├─ categories     (Categorias de transações)
          │   └─ transactions   (Transações financeiras)
          └─ 📋 System Info
```

## 📊 Estrutura das Tabelas

### 1. **accounts** - Contas Bancárias/Carteiras
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| name | VARCHAR(120) | Nome da conta |
| type | VARCHAR(40) | Tipo: BANK, CASH, CREDIT_CARD, etc. |
| active | BOOLEAN | Conta ativa (soft delete) |
| created_at | DATETIME | Data de criação |

### 2. **categories** - Categorias
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| name | VARCHAR(120) | Nome da categoria (único) |
| kind | VARCHAR(20) | INCOME ou EXPENSE |
| group | VARCHAR(20) | ESSENTIAL, LIFESTYLE, FUTURE, OTHER |
| active | BOOLEAN | Categoria ativa (soft delete) |

### 3. **transactions** - Transações
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| date | DATE | Data da transação |
| description | VARCHAR(255) | Descrição |
| amount | NUMERIC(12,2) | Valor (positivo=receita, negativo=despesa) |
| kind | VARCHAR(20) | INCOME, EXPENSE ou TRANSFER |
| account_id | INTEGER | FK para accounts |
| category_id | INTEGER | FK para categories (nullable) |
| transfer_pair_id | VARCHAR(36) | UUID para ligar transferências |
| created_at | DATETIME | Data de criação |

### 4. **budgets** - Orçamentos Mensais
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| month | VARCHAR(7) | Formato: YYYY-MM |
| category_id | INTEGER | FK para categories |
| amount_planned | NUMERIC(12,2) | Valor planejado (positivo) |

## 🔍 Queries Úteis

### Ver todas as contas ativas
```sql
SELECT * FROM accounts WHERE active = 1;
```

### Ver transações de um período
```sql
SELECT 
    t.date,
    t.description,
    t.amount,
    t.kind,
    a.name AS account_name,
    c.name AS category_name
FROM transactions t
LEFT JOIN accounts a ON t.account_id = a.id
LEFT JOIN categories c ON t.category_id = c.id
WHERE t.date BETWEEN '2026-01-01' AND '2026-01-31'
ORDER BY t.date DESC;
```

### Ver saldo total por conta
```sql
SELECT 
    a.name AS account,
    SUM(t.amount) AS balance
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id
WHERE a.active = 1
GROUP BY a.id, a.name
ORDER BY balance DESC;
```

### Ver orçamento vs realizado (mês atual)
```sql
SELECT 
    c.name AS category,
    b.amount_planned,
    COALESCE(SUM(ABS(t.amount)), 0) AS amount_spent,
    b.amount_planned - COALESCE(SUM(ABS(t.amount)), 0) AS difference
FROM budgets b
JOIN categories c ON b.category_id = c.id
LEFT JOIN transactions t ON t.category_id = c.id 
    AND strftime('%Y-%m', t.date) = b.month
    AND t.kind = 'EXPENSE'
WHERE b.month = '2026-01'
GROUP BY c.id, c.name, b.amount_planned
ORDER BY difference ASC;
```

### Ver transferências com seus pares
```sql
SELECT 
    t.transfer_pair_id,
    t.date,
    t.description,
    t.amount,
    a.name AS account_name,
    CASE 
        WHEN t.amount < 0 THEN 'Saída'
        ELSE 'Entrada'
    END AS direction
FROM transactions t
JOIN accounts a ON t.account_id = a.id
WHERE t.kind = 'TRANSFER'
    AND t.transfer_pair_id IS NOT NULL
ORDER BY t.transfer_pair_id, t.amount;
```

## 🛠️ Operações Comuns no DBeaver

### Visualizar Dados
- Duplo clique na tabela → Aba **Data**
- Clique com botão direito → **View Data**

### Exportar Dados
1. Clique com botão direito na tabela
2. **Export Data** → Escolha o formato (CSV, JSON, XML, etc.)

### Executar Queries
1. Clique com botão direito na conexão → **SQL Editor** → **New SQL Script**
2. Escreva sua query
3. Pressione `Ctrl+Enter` para executar

### Ver Diagrama ER
1. Clique com botão direito em **Tables**
2. **View Diagram**
3. Selecione todas as tabelas
4. O DBeaver gerará o diagrama de relacionamentos automaticamente

## ⚠️ Considerações Importantes

### 1. **Banco em Uso**
Se a aplicação estiver rodando (`uvicorn`), o SQLite pode bloquear algumas operações de escrita no DBeaver devido a limitações de concorrência. Recomendações:
- Para **apenas visualizar**: pode deixar a aplicação rodando
- Para **modificar dados**: pare a aplicação primeiro

### 2. **Backup Antes de Modificar**
Sempre faça backup antes de modificar dados diretamente:
```powershell
# Criar backup
copy app.db app.db.backup

# Restaurar backup se necessário
copy app.db.backup app.db
```

### 3. **Não Modificar alembic_version**
Nunca altere manualmente a tabela `alembic_version` - ela controla as migrações do banco de dados.

### 4. **Cuidado com Constraints**
Respeite as constraints ao inserir/modificar dados:
- **Unique**: `categories.name` deve ser único
- **Foreign Keys**: IDs devem existir nas tabelas referenciadas
- **Check Constraints**: 
  - `transactions.amount` positivo para INCOME, negativo para EXPENSE
  - `budgets.amount_planned` deve ser positivo

## 🔄 Alternativas ao DBeaver

### SQLite Browser (mais leve)
```
https://sqlitebrowser.org/
```

### VSCode Extension: SQLite Viewer
1. Instale a extensão **SQLite Viewer** no VSCode
2. Clique com botão direito em `app.db` → **Open Database**

### CLI do SQLite (linha de comando)
```powershell
# Abrir banco
sqlite3 app.db

# Listar tabelas
.tables

# Ver schema
.schema accounts

# Executar query
SELECT * FROM accounts;

# Sair
.exit
```

## 📚 Recursos Adicionais

- **Documentação DBeaver**: https://dbeaver.io/docs/
- **SQLite Syntax**: https://www.sqlite.org/lang.html
- **Alembic (Migrations)**: https://alembic.sqlalchemy.org/

---

**Configurado e pronto para explorar seus dados financeiros! 🎉**
