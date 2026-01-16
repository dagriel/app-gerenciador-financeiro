"""Architecture guardrails (layer dependency rules).

Objetivo: evitar “drift” arquitetural conforme o projeto cresce.

Esses testes não substituem revisão de código, mas ajudam a:
- manter Domain puro (sem FastAPI/SQLAlchemy)
- manter Routers finos (sem repositories/db.session)
- evitar commit/rollback fora do boundary (get_uow)

Regras aqui são pragmáticas para o MVP, mas com uma regra forte:
Domain não deve depender de `app.core` (core é apenas compatibilidade/shim).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "app"


@dataclass(frozen=True)
class Violation:
    file: str
    lineno: int
    layer: str
    imported: str
    rule: str


def _iter_py_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if p.is_file()]


def _layer_for_file(path: Path) -> str:
    rel = path.relative_to(SRC_ROOT).as_posix()
    top = rel.split("/", 1)[0]
    return top  # api, services, domain, repositories, db, core, schemas, ...


def _extract_imports(path: Path) -> list[tuple[int, str]]:
    """Return list of (lineno, module) for imports in a python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.lineno, node.module))
    return imports


def _is_prefix(mod: str, prefixes: tuple[str, ...]) -> bool:
    return any(mod == p or mod.startswith(p + ".") for p in prefixes)


def test_layer_dependencies() -> None:
    """Enforce high-level layer dependency rules."""
    violations: list[Violation] = []

    # Pragmatic rules for this project (MVP).
    DOMAIN_FORBIDDEN = (
        "app.api",
        "app.services",
        "app.repositories",
        "app.db",
        "app.core",
        "fastapi",
        "starlette",
        "sqlalchemy",
    )
    SERVICES_FORBIDDEN = (
        "app.api",  # keep HTTP layer out of use-cases
        "fastapi",
        "starlette",
    )
    REPOS_FORBIDDEN = (
        "app.api",
        "app.services",
        "fastapi",
        "starlette",
    )
    # API "global" (ex.: api/deps.py) pode conhecer db/session porque é o boundary/DI.
    API_FORBIDDEN = (
        "app.repositories",  # API não deve falar direto com repos (routers -> services)
        "sqlalchemy",
    )
    # Routers devem ser finos: não criam sessão diretamente.
    API_ROUTERS_FORBIDDEN = ("app.db.session",)

    for file_path in _iter_py_files(SRC_ROOT):
        layer = _layer_for_file(file_path)
        for lineno, mod in _extract_imports(file_path):
            if layer == "domain" and _is_prefix(mod, DOMAIN_FORBIDDEN):
                violations.append(
                    Violation(
                        file=str(file_path.relative_to(SRC_ROOT)),
                        lineno=lineno,
                        layer=layer,
                        imported=mod,
                        rule=f"domain must not import {DOMAIN_FORBIDDEN}",
                    )
                )
            if layer == "services" and _is_prefix(mod, SERVICES_FORBIDDEN):
                violations.append(
                    Violation(
                        file=str(file_path.relative_to(SRC_ROOT)),
                        lineno=lineno,
                        layer=layer,
                        imported=mod,
                        rule=f"services must not import {SERVICES_FORBIDDEN}",
                    )
                )
            if layer == "repositories" and _is_prefix(mod, REPOS_FORBIDDEN):
                violations.append(
                    Violation(
                        file=str(file_path.relative_to(SRC_ROOT)),
                        lineno=lineno,
                        layer=layer,
                        imported=mod,
                        rule=f"repositories must not import {REPOS_FORBIDDEN}",
                    )
                )
            if layer == "api":
                rel = file_path.relative_to(SRC_ROOT).as_posix()
                is_router = rel.startswith("api/routers/")
                if _is_prefix(mod, API_FORBIDDEN):
                    violations.append(
                        Violation(
                            file=str(file_path.relative_to(SRC_ROOT)),
                            lineno=lineno,
                            layer=layer,
                            imported=mod,
                            rule=f"api must not import {API_FORBIDDEN}",
                        )
                    )
                if is_router and _is_prefix(mod, API_ROUTERS_FORBIDDEN):
                    violations.append(
                        Violation(
                            file=str(file_path.relative_to(SRC_ROOT)),
                            lineno=lineno,
                            layer=layer,
                            imported=mod,
                            rule=f"api routers must not import {API_ROUTERS_FORBIDDEN}",
                        )
                    )

    assert not violations, "Layer dependency violations:\n" + "\n".join(
        f"- {v.file}:{v.lineno} [{v.layer}] imports '{v.imported}' ({v.rule})" for v in violations
    )


def test_no_commit_or_rollback_outside_boundary() -> None:
    """Prevent commit/rollback usage in services/repositories (should be in get_uow/boundary)."""
    violations: list[str] = []

    def scan_dir(dir_name: str) -> None:
        for file_path in _iter_py_files(SRC_ROOT / dir_name):
            text = file_path.read_text(encoding="utf-8")
            # Cheap-but-effective checks (avoid false positives on docs/strings where possible)
            if ".commit(" in text:
                violations.append(
                    f"{dir_name}/{file_path.name}: contains '.commit('"
                    " (services/repos must not commit)"
                )
            if ".rollback(" in text:
                violations.append(
                    f"{dir_name}/{file_path.name}: contains '.rollback('"
                    " (services/repos must not rollback)"
                )

    scan_dir("services")
    scan_dir("repositories")

    assert not violations, "Commit/Rollback violations:\n" + "\n".join(f"- {v}" for v in violations)
