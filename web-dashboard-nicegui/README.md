# web-dashboard-nicegui

Dashboard web (NiceGUI) para consumir a API **APP-GERENCIADOR-FINANCEIRO** de forma **server-side** (BFF local), usando `httpx` + `X-API-Key` no backend da UI.

## ✅ Por que NiceGUI (server-side)

- **Sem CORS**: o browser fala com o NiceGUI; o NiceGUI chama a API.
- **Não expõe API key** no JavaScript do navegador.
- Permite UI rápida para listagens, filtros, formulários e dashboards.
- Arquitetura preparada para evoluir (camadas, client HTTP central, contrato de erro).

---

## 📦 Requisitos

- Python **3.13+**
- Backend da API rodando (por padrão em `http://127.0.0.1:8000`)

---

## ⚙️ Configuração

### 1) Crie o `.env` do dashboard

Copie o exemplo:

```powershell
copy .env.example .env
```

Edite `.env` e ajuste:

- `FIN_API_BASE_URL` (URL da API)
- `FIN_API_KEY` (mesma chave do backend)
- `DASHBOARD_PORT` (porta da UI)

> Observação: `.env` é ignorado pelo `.gitignore`.

### 2) Instale dependências (recomendado em venv separado)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Se o comando "pip" não existir no seu terminal, use sempre:
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

> Alternativa (sem depender do activate):  
> `.\.venv\Scripts\python.exe -m pip install -U pip`  
> `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`

---

## ▶️ Executar

> Recomendado: rode o backend **em um terminal** e o dashboard **em outro**.

### Backend (API)

Na raiz do repositório:

```powershell
uvicorn app.main:app --reload
```

### Dashboard (NiceGUI)

Dentro de `web-dashboard-nicegui/`:

```powershell
python -m dashboard_nicegui
```

> Se você ainda não ativou a venv (ou quer garantir 100%):
> `.\.venv\Scripts\python.exe -m dashboard_nicegui`

A UI sobe em: `http://127.0.0.1:8081` (ou a porta do seu `.env`).

---

## 🧭 Páginas (MVP)

- **Dashboard**: resumo mensal + orçado vs realizado (`/`)
- **Transações**: (stub inicial, evoluir)
- **Orçamentos**: (stub inicial, evoluir)
- **Contas**: (stub inicial, evoluir)
- **Categorias**: (stub inicial, evoluir)

---

## 🧱 Estrutura (camadas)

```
src/dashboard_nicegui/
  main.py                # bootstrap NiceGUI + layout + rotas
  core/
    settings.py          # config (pydantic-settings + dotenv)
    errors.py            # ProblemDetail + exceções
    logging.py           # logging básico
  api_client/
    client.py            # httpx AsyncClient + wrapper tipado
    dtos.py              # DTOs pydantic dos endpoints usados na UI
  features/
    dashboard/page.py
    ...
  shared/
    formatters.py
    components.py
```

---

## 🧯 Contrato de erros (ProblemDetail)

A API retorna erros padronizados (ProblemDetail). O dashboard:
- tenta parsear `code` e `detail`
- exibe mensagens previsíveis para o usuário (toast)
- mantém logs do erro no server-side

---

## 🧪 Qualidade

- `ruff check .`
- `ruff format .`
- `pytest`
