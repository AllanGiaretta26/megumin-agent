"""Ferramentas de acesso ao sistema de arquivos disponíveis ao agente.

Tool calling é o mecanismo pelo qual o LLM "pede" ao sistema que execute uma ação
real — como ler um arquivo — em vez de apenas falar sobre ela. Funciona assim:
  1. Descrevemos as tools com nome + descrição (esse texto é o "cardápio" que o LLM lê).
  2. Vinculamos as tools ao LLM via llm.bind_tools(tools).
  3. O LLM, ao decidir que precisa de informação, gera uma AIMessage com tool_calls.
  4. O ToolNode do LangGraph executa a tool chamada e devolve um ToolMessage com o resultado.
  5. O LLM recebe o resultado e continua o raciocínio.

O campo `project_path` em cada tool usa InjectedState — o LLM nunca vê esse
parâmetro no schema, o ToolNode o injeta automaticamente a partir do estado do grafo.
"""
from langchain_core.tools import BaseTool

from .list_directory import list_directory
from .read_file import read_file
from .write_file import write_file

_TOOL_REGISTRY: dict[str, BaseTool] = {
    "read_file": read_file,
    "list_directory": list_directory,
    "write_file": write_file,
}


def get_tools_by_names(names: list[str]) -> list[BaseTool]:
    """Retorna as instâncias de tool correspondentes aos nomes solicitados."""
    return [_TOOL_REGISTRY[name] for name in names if name in _TOOL_REGISTRY]


__all__ = ["read_file", "list_directory", "write_file", "get_tools_by_names"]
