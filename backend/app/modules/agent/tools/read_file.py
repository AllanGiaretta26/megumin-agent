from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger

from .base import ToolResult


def _read_file_impl(path: str, project_path: str) -> ToolResult:
    """Lógica pura do read_file — testável sem LangChain.

    Retorna ToolResult com status explícito. Não levanta PathTraversalError
    (captura e converte em ToolResult error). Outras exceções de I/O
    ainda propagam (dívida #21).
    """
    logger.info(f"[tool] read_file | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        if not safe_path.exists():
            return ToolResult(status="error", content=f"Arquivo não encontrado: '{path}'")
        if not safe_path.is_file():
            return ToolResult(status="error", content=f"'{path}' não é um arquivo.")
        return ToolResult(status="ok", content=safe_path.read_text(encoding="utf-8", errors="replace"))
    except PathTraversalError as exc:
        logger.error(f"[tool] read_file bloqueado: {exc}")
        return ToolResult(status="error", content=f"Acesso negado: {exc}")


@tool(response_format="content_and_artifact")
def read_file(
    path: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> tuple[str, ToolResult]:
    """Lê o conteúdo de um arquivo dentro do project_path.

    Args:
        path: Caminho relativo ao project_path do arquivo a ser lido.
    """
    result = _read_file_impl(path, project_path)
    return result.content, result
