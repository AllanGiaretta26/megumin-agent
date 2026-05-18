from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger

from .base import ToolResult

_IGNORED = {".git", "__pycache__", "node_modules", ".venv"}


def _list_directory_impl(path: str, project_path: str) -> ToolResult:
    """Lógica pura do list_directory — testável sem LangChain.

    Retorna ToolResult com status explícito. Não levanta PathTraversalError
    (captura e converte em ToolResult error). Outras exceções de I/O
    ainda propagam (dívida #21).
    """
    logger.info(f"[tool] list_directory | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        if not safe_path.exists():
            return ToolResult(status="error", content=f"Diretório não encontrado: '{path}'")
        if not safe_path.is_dir():
            return ToolResult(status="error", content=f"'{path}' não é um diretório.")

        entries = sorted(safe_path.iterdir(), key=lambda p: (p.is_file(), p.name))
        lines = []
        for entry in entries:
            if entry.name in _IGNORED:
                continue
            prefix = "  " if entry.is_file() else "📁"
            lines.append(f"{prefix} {entry.name}")

        content = "\n".join(lines) if lines else "(diretório vazio)"
        return ToolResult(status="ok", content=content)
    except PathTraversalError as exc:
        logger.error(f"[tool] list_directory bloqueado: {exc}")
        return ToolResult(status="error", content=f"Acesso negado: {exc}")


@tool(response_format="content_and_artifact")
def list_directory(
    path: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> tuple[str, ToolResult]:
    """Lista arquivos e diretórios dentro de um caminho no project_path.

    Args:
        path: Caminho relativo ao project_path do diretório a listar. Use "." para a raiz.
    """
    result = _list_directory_impl(path, project_path)
    return result.content, result
