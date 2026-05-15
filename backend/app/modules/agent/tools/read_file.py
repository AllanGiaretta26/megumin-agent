from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger


@tool
def read_file(
    path: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> str:
    """Lê o conteúdo de um arquivo dentro do project_path.

    Args:
        path: Caminho relativo ao project_path do arquivo a ser lido.
    """
    logger.info(f"[tool] read_file | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        if not safe_path.exists():
            return f"Arquivo não encontrado: '{path}'"
        if not safe_path.is_file():
            return f"'{path}' não é um arquivo."
        return safe_path.read_text(encoding="utf-8", errors="replace")
    except PathTraversalError as exc:
        logger.error(f"[tool] read_file bloqueado: {exc}")
        return f"Acesso negado: {exc}"
