"""Tipos compartilhados pelas tools do agente.

`ToolResult` é o contrato interno que cada tool retorna. Substitui a
heurística antiga `output.startswith("error")` por status explícito.

Fluxo:
  tool function → ToolResult → tupla (content, ToolResult) via @tool
  → LangChain monta ToolMessage(content=content, artifact=ToolResult)
  → grafo lê artifact.status no on_tool_end

Dívida #21 — Tools ainda não capturam OSError/PermissionError/
UnicodeDecodeError de I/O real. Exceções de baixo nível propagam para
fora da tool e viram erro 500 no grafo. Tratar quando virar prioridade.

Dívida #24 — Modelo gera pseudo-tool-call como JSON em texto em vez
de invocar a tool real (observado com gpt-oss:120b em modo Agente).
Prioridade média. Possíveis caminhos: prompt do modo mais firme contra
"escrever JSON de tool na resposta", temperature mais baixa em modo
agentic, ou troca de modelo.

Dívida #26 — gpt-oss:120b ocasionalmente devolve pseudo-tool-call em
texto em vez de structured tool_calls. Observado durante a Sub-tarefa 3
do Passo 1 da estabilização, não reproduzível em 5/5 retentativas no
mesmo dia — provavelmente característica do modelo / Ollama Cloud.
Mitigação futura: trocar para modelo com melhor function calling, ou
adicionar retry com prompt reforçado quando AIMessage.tool_calls vier
vazio mas content contiver JSON estruturado. Prioridade média.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Resultado estruturado de uma tool. Imutável."""

    status: Literal["ok", "error"]
    content: str
