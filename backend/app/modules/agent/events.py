"""Contrato tipado dos eventos que saem do gerador do grafo.

Substitui o `str | dict` solto que o `astream` yieldava antes. Modela só
o que vem do domínio do agente — os eventos de transporte SSE (`done`,
`error`) continuam construídos no router.

Wire-name vs. class-name:
  - `TextChunkEvent.type == "token"` (wire mantém "token" por compat
    com o frontend, já registrado nos eventos enviados ao SSE).
  - `ToolResultEvent.type == "tool_call"` — o nome no wire é misnomer
    (carrega o RESULTADO da tool, não a chamada), preservado para não
    quebrar o frontend. Dívida #25 — rename coordenado em PR futuro.

Serialização:
  `to_sse_data()` usa `json.dumps(self.model_dump())` (não
  `model_dump_json()`) para preservar paridade byte-a-byte com a
  serialização legada via `json.dumps(dict)`. Defaults de Unicode escape
  diferem entre os dois caminhos.
"""
import json
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class TextChunkEvent(BaseModel):
    """Token de texto do LLM ou bloco completo do fallback format_response."""

    type: Literal["token"] = "token"
    content: str

    def to_sse_data(self) -> str:
        return f"data: {json.dumps(self.model_dump())}\n\n"


class ToolResultEvent(BaseModel):
    """Resultado de execução de uma tool, com status explícito.

    Campos na mesma ordem do dict legado em graph.py para preservar
    insertion order na serialização (frontend pode depender disso).
    """

    type: Literal["tool_call"] = "tool_call"
    tool: str
    args: dict
    output: str
    status: Literal["ok", "error"]

    def to_sse_data(self) -> str:
        return f"data: {json.dumps(self.model_dump())}\n\n"


AgentEvent = Annotated[
    Union[TextChunkEvent, ToolResultEvent],
    Field(discriminator="type"),
]
