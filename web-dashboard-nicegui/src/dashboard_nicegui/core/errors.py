from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ProblemDetail(BaseModel):
    """Contrato de erro padrão (compatível com o backend).

    Backend (FastAPI) usa ProblemDetail inspirado no RFC 7807 e inclui `code` e `errors`
    para casos como validação (422).
    """

    model_config = ConfigDict(extra="ignore")

    status: int
    title: str
    detail: str
    code: str | None = None
    instance: str | None = None
    errors: list[dict[str, Any]] | None = None


class ApiProblemError(RuntimeError):
    """Erro levantado quando a API retorna ProblemDetail (4xx/5xx)."""

    def __init__(self, problem: ProblemDetail):
        self.problem = problem
        super().__init__(self.human_message)

    @property
    def human_message(self) -> str:
        # Formato curto e estável para UI/logs.
        if self.problem.code:
            return f"{self.problem.code}: {self.problem.detail}"
        return self.problem.detail


class ApiUnexpectedResponseError(RuntimeError):
    """Erro quando a API retorna payload inesperado/não parseável."""

    def __init__(self, *, status_code: int | None, body_excerpt: str):
        self.status_code = status_code
        self.body_excerpt = body_excerpt
        super().__init__(f"Resposta inesperada da API (status={status_code}): {body_excerpt}")


def try_parse_problem_detail(data: Any) -> ProblemDetail | None:
    """Tenta interpretar um payload como ProblemDetail (sem levantar)."""
    if not isinstance(data, dict):
        return None
    if "status" not in data or "title" not in data or "detail" not in data:
        return None
    try:
        return ProblemDetail.model_validate(data)
    except Exception:
        return None


def map_problem_code_to_user_message(code: str) -> str | None:
    """Mapeia códigos estáveis (ErrorMessage.name) para mensagens amigáveis.

    Mantemos um mapping mínimo no MVP. Se o code não estiver no mapping,
    a UI cai no `detail` vindo do backend (já é em pt-BR).
    """
    mapping = {
        "API_KEY_INVALID": "API key inválida. Verifique FIN_API_KEY no .env do dashboard.",
    }
    return mapping.get(code)
