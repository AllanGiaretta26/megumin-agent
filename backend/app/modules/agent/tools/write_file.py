from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger


@tool
def write_file(
    path: str,
    content: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> str:
    """Escreve ou sobrescreve um arquivo dentro do project_path.

    Args:
        path: Caminho relativo ao project_path onde o arquivo será criado/sobrescrito.
        content: Conteúdo completo a ser escrito no arquivo.
    """
    logger.info(f"[tool] write_file | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding="utf-8")
        logger.info(f"[tool] write_file concluído | path={safe_path}")
        return f"Arquivo '{path}' escrito com sucesso ({len(content)} caracteres)."
    except PathTraversalError as exc:
        logger.error(f"[tool] write_file bloqueado: {exc}")
        return f"Acesso negado: {exc}"
