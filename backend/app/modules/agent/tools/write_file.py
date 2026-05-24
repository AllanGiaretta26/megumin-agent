from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger

from .base import ToolResult, io_error_result


def _write_file_impl(path: str, content: str, project_path: str) -> ToolResult:
    """Lógica pura do write_file — testável sem LangChain.

    Retorna ToolResult com status explícito. Não levanta PathTraversalError
    nem OSError de I/O real (captura e converte em ToolResult error).
    """
    logger.info(f"[tool] write_file | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        logger.info(f"[tool] write_file concluído | path={safe_path}")
        msg = f"Arquivo '{path}' escrito com sucesso ({len(content)} caracteres)."
        return ToolResult(status="ok", content=msg)
    except PathTraversalError as exc:
        logger.error(f"[tool] write_file bloqueado: {exc}")
        return ToolResult(status="error", content=f"Acesso negado: {exc}")
    except OSError as exc:
        return io_error_result("write_file", path, exc)


@tool(response_format="content_and_artifact")
def write_file(
    path: str,
    content: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> tuple[str, ToolResult]:
    """Escreve ou sobrescreve um arquivo dentro do project_path.

    Args:
        path: Caminho relativo ao project_path onde o arquivo será criado/sobrescrito.
        content: Conteúdo completo a ser escrito no arquivo.
    """
    result = _write_file_impl(path, content, project_path)
    return result.content, result
