from langchain_core.messages import SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.core.exceptions import ModeNotFoundError, OllamaUnavailableError
from app.shared.logger import logger

from .modes import from_name as mode_from_name
from .providers.base import BaseLLMProvider
from .providers.ollama import OllamaProvider
from .state import AgentState
from .tools import get_tools_by_names, list_directory, read_file, write_file

# Lista completa de tools que o ToolNode pode executar.
# O ToolNode precisa de todas registradas — a filtragem por modo ocorre
# em _call_llm_with_tools (via bind_tools), não aqui.
_ALL_TOOLS = [read_file, list_directory, write_file]


def _select_mode(state: AgentState) -> dict:
    """Nó 1: carrega a configuração do modo a partir de state['mode'].

    Este nó precisa existir ANTES do call_llm porque o system_prompt e
    allowed_tools variam por modo — o LLM precisa dessas informações antes
    de gerar qualquer resposta. É o equivalente a um middleware de configuração
    que prepara o contexto antes da execução principal.
    """
    logger.info(f"[grafo] select_mode | mode={state['mode']}")
    try:
        mode = mode_from_name(state["mode"])
    except ModeNotFoundError:
        raise

    return {
        "allowed_tools": mode.allowed_tools,
        "system_prompt": mode.system_prompt,
    }


def _make_call_llm_node(provider: BaseLLMProvider):
    """Factory que retorna o nó call_llm capturando o provider via closure."""

    def _call_llm_with_tools(state: AgentState) -> dict:
        """Nó 2: invoca o LLM com system prompt + histórico + tools do modo.

        A diferença em relação à Fase 3: agora vinculamos tools ao LLM via
        bind_tools. O LLM recebe os schemas das tools e pode gerar uma
        AIMessage com tool_calls em vez de texto direto.
        """
        tools = get_tools_by_names(state["allowed_tools"])
        llm = provider.get_llm_with_tools(tools) if tools else provider.get_llm()

        # O system_prompt vai à frente das mensagens de conversa, mas NÃO é
        # salvo em state["messages"] — é um campo separado para evitar
        # que ele se acumule a cada iteração do loop ReAct.
        system_msg = SystemMessage(content=state["system_prompt"])
        all_messages = [system_msg] + list(state["messages"])

        logger.info(
            f"[grafo] call_llm | mode={state['mode']} "
            f"tools={state['allowed_tools']} msgs={len(all_messages)}"
        )

        try:
            response = llm.invoke(all_messages)
        except Exception as exc:
            logger.error(f"[grafo] Erro ao invocar LLM: {exc}")
            raise OllamaUnavailableError(
                f"Ollama não está disponível em {provider.get_llm().base_url}."
            ) from exc

        # add_messages no estado acumula automaticamente — apenas retornamos a nova msg
        return {"messages": [response]}

    return _call_llm_with_tools


def _route_after_llm(state: AgentState) -> str:
    """Edge condicional: decide o próximo nó após o LLM responder.

    Se a última mensagem tiver tool_calls, o LLM pediu para executar uma tool.
    Caso contrário, a resposta é texto final e podemos encerrar.
    """
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        logger.debug(f"[grafo] LLM solicitou tools: {[tc['name'] for tc in last.tool_calls]}")
        return "execute_tools"
    return "format_response"


def _format_response(state: AgentState) -> dict:
    """Nó 4: extrai o texto final da última AIMessage como response.

    Na Fase 7 aqui entrará o ajuste de drama_level antes de devolver.
    """
    last = state["messages"][-1]
    return {"response": str(last.content)}


def _build_graph(provider: BaseLLMProvider):
    """Compila o StateGraph com o loop ReAct completo.

    Fluxo:
      select_mode → call_llm_with_tools ──(tool_calls?)──→ execute_tools ──→ call_llm_with_tools
                                         └──(sem tools)──→ format_response → END
    """
    tool_node = ToolNode(_ALL_TOOLS)

    builder = StateGraph(AgentState)
    builder.add_node("select_mode", _select_mode)
    builder.add_node("call_llm_with_tools", _make_call_llm_node(provider))
    builder.add_node("execute_tools", tool_node)
    builder.add_node("format_response", _format_response)

    builder.set_entry_point("select_mode")
    builder.add_edge("select_mode", "call_llm_with_tools")
    builder.add_conditional_edges("call_llm_with_tools", _route_after_llm)
    builder.add_edge("execute_tools", "call_llm_with_tools")
    builder.add_edge("format_response", END)

    return builder.compile()


class AgentService:
    """Orquestra a execução do agente via LangGraph."""

    def __init__(self, provider: BaseLLMProvider | None = None) -> None:
        self._graph = _build_graph(provider or OllamaProvider())

    def run(
        self,
        messages: list,
        session_id: str,
        mode: str = "study",
        project_path: str = "",
    ) -> str:
        """Executa o grafo e retorna o texto da resposta final."""
        logger.info(f"[agente] run | session={session_id} mode={mode}")
        initial_state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "response": "",
            "mode": mode,
            "project_path": project_path,
            "allowed_tools": [],
            "system_prompt": "",
        }
        result = self._graph.invoke(initial_state)
        return result["response"]
