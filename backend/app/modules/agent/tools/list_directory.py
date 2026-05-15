from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.core.exceptions import PathTraversalError
from app.core.security import validate_path
from app.shared.logger import logger

_IGNORED = {".git", "__pycache__", "node_modules", ".venv"}


@tool
def list_directory(
    path: str,
    project_path: Annotated[str, InjectedState("project_path")],
) -> str:
    """Lista arquivos e diretórios dentro de um caminho no project_path.

    Args:
        path: Caminho relativo ao project_path do diretório a listar. Use "." para a raiz.
    """
    logger.info(f"[tool] list_directory | path={path}")
    try:
        safe_path = validate_path(path, project_path)
        if not safe_path.exists():
            return f"Diretório não encontrado: '{path}'"
        if not safe_path.is_dir():
            return f"'{path}' não é um diretório."

        entries = sorted(safe_path.iterdir(), key=lambda p: (p.is_file(), p.name))
        lines = []
        for entry in entries:
            if entry.name in _IGNORED:
                continue
            prefix = "  " if entry.is_file() else "📁"
            lines.append(f"{prefix} {entry.name}")

        return "\n".join(lines) if lines else "(diretório vazio)"
    except PathTraversalError as exc:
        logger.error(f"[tool] list_directory bloqueado: {exc}")
        return f"Acesso negado: {exc}"
