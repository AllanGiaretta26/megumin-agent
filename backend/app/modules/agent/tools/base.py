"""Tipos compartilhados pelas tools do agente.

`ToolResult` é o contrato interno que cada tool retorna. Substitui a
heurística antiga `output.startswith("error")` por status explícito.

Fluxo:
  tool function → ToolResult → tupla (content, ToolResult) via @tool
  → LangChain monta ToolMessage(content=content, artifact=ToolResult)
  → grafo lê artifact.status no on_tool_end
"""
from dataclasses import dataclass
from typing import Literal

from app.shared.logger import logger


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Resultado estruturado de uma tool. Imutável."""

    status: Literal["ok", "error"]
    content: str


def io_error_result(tool_name: str, path: str, exc: OSError) -> ToolResult:
    """Converte falhas reais de filesystem em erro estruturado da tool."""

    logger.exception(f"[tool] {tool_name} erro de I/O | path={path}")
    if isinstance(exc, PermissionError):
        return ToolResult(status="error", content=f"Acesso negado: {exc}")
    return ToolResult(status="error", content=f"Erro de I/O em '{path}': {exc}")
