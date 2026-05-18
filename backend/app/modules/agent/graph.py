from collections.abc import AsyncIterator
from pathlib import Path

from langchain_core.messages import SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_PERSONALITY_TEMPLATE = (_PROMPTS_DIR / "personality.md").read_text(encoding="utf-8")

from app.core.exceptions import ModeNotFoundError, OllamaUnavailableError
from app.modules.config.schemas import AppConfig
from app.shared import render_template
from app.shared.logger import logger

from .events import AgentEvent, TextChunkEvent, ToolResultEvent
from .modes import from_name as mode_from_name
from .providers import build_provider
from .providers.base import BaseLLMProvider
from .state import AgentState
from .tools import get_tools_by_names, list_directory, read_file, write_file
from .tools.base import ToolResult

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
    logger.info(
        f"[grafo] select_mode | mode={state['mode']} "
        f"drama={state['drama_level']} lang={state['language']}"
    )
    try:
        mode = mode_from_name(state["mode"])
    except ModeNotFoundError:
        raise

    if state["drama_level"] == 0:
        return {"allowed_tools": mode.allowed_tools, "system_prompt": mode.system_prompt}

    personality = render_template(
        _PERSONALITY_TEMPLATE,
        drama_level=state["drama_level"],
        language=state["language"],
    )
    # Personalidade vem ANTES do prompt de modo: modelos 8B-9B ancoram
    # identidade no primeiro parágrafo do system prompt.
    full_prompt = personality + "\n\n" + mode.system_prompt

    return {
        "allowed_tools": mode.allowed_tools,
        "system_prompt": full_prompt,
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
            f"[grafo] call_llm | mode={state['mode']} drama={state['drama_level']} "
            f"tools={state['allowed_tools']} msgs={len(all_messages)}"
        )
        # Log dos primeiros 300 chars do system prompt para confirmar que a personalidade chega ao LLM
        logger.info(f"[grafo] system_prompt preview: {state['system_prompt'][:300]!r}")

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
        tool_names = [tc["name"] for tc in last.tool_calls]
        logger.info(f"[grafo] → execute_tools | tools={tool_names}")
        return "execute_tools"
    logger.info(f"[grafo] → format_response")
    return "format_response"


def _format_response(state: AgentState) -> dict:
    """Nó 4: extrai o texto final da última AIMessage como response."""
    last = state["messages"][-1]
    content = str(last.content)
    logger.info(f"[grafo] format_response | content_len={len(content)}")
    return {"response": content}


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

    def __init__(self, config: AppConfig) -> None:
        self._provider = build_provider(config)
        self._graph = _build_graph(self._provider)

    def run(
        self,
        messages: list,
        session_id: str,
        mode: str = "free_chat",
        project_path: str = "",
        drama_level: int = 50,
        language: str = "pt-BR",
    ) -> str:
        """Executa o grafo e retorna o texto da resposta final."""
        logger.info(
            f"[agente] run | session={session_id} mode={mode} "
            f"drama={drama_level} lang={language}"
        )
        initial_state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "response": "",
            "mode": mode,
            "project_path": project_path,
            "allowed_tools": [],
            "system_prompt": "",
            "drama_level": drama_level,
            "language": language,
        }
        result = self._graph.invoke(initial_state)
        return result["response"]

    async def astream(
        self,
        messages: list,
        session_id: str,
        mode: str = "free_chat",
        project_path: str = "",
        drama_level: int = 50,
        language: str = "pt-BR",
    ) -> AsyncIterator[AgentEvent]:
        """Async generator que emite eventos tipados (TextChunkEvent /
        ToolResultEvent) do domínio do agente.

        Quando o Ollama não suporta streaming após tool_use (limitação conhecida),
        on_chat_model_stream não dispara para a resposta final. O fallback captura
        o output de format_response via on_chain_end e emite o texto inteiro
        como um TextChunkEvent só.

        ValidationError NÃO é capturado: se algum ramo tentar construir um
        evento com payload fora do contrato, a exception sobe (Ajuste 2 do
        plano — fallback ruidoso).
        """
        logger.info(
            f"[agente] astream | session={session_id} mode={mode} "
            f"drama={drama_level} lang={language}"
        )
        initial_state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "response": "",
            "mode": mode,
            "project_path": project_path,
            "allowed_tools": [],
            "system_prompt": "",
            "drama_level": drama_level,
            "language": language,
        }

        tokens_emitted: list[str] = []

        async for event in self._graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            name = event.get("name", "")

            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                # chunk.content é string vazia em tool_call_chunks — ignorar
                if hasattr(chunk, "content") and chunk.content:
                    token = str(chunk.content)
                    tokens_emitted.append(token)
                    yield TextChunkEvent(content=token)

            elif kind == "on_tool_end":
                tool_name = event.get("name", "unknown")
                tool_input = event.get("data", {}).get("input", {})
                tool_output = event.get("data", {}).get("output")

                # output pode ser ToolMessage (caminho novo, com .artifact) ou
                # string nua (tools ainda não migradas) — normalizar conteúdo.
                if hasattr(tool_output, "content"):
                    output_str = str(tool_output.content)
                else:
                    output_str = str(tool_output) if tool_output is not None else ""

                # Status vem do ToolResult anexado como artifact da ToolMessage.
                # Fallback ruidoso: se artifact não for ToolResult (tool não migrada
                # ou LangChain não expôs), default é "error" + log — assumir "ok"
                # repete a cegueira da heurística antiga.
                artifact = getattr(tool_output, "artifact", None)
                if isinstance(artifact, ToolResult):
                    status = artifact.status
                else:
                    logger.error(
                        f"[agente] tool {tool_name!r} não devolveu ToolResult como "
                        f"artifact (artifact={type(artifact).__name__}). Marcando "
                        f"status=error por segurança."
                    )
                    status = "error"

                logger.info(
                    f"[agente] astream tool_end | tool={tool_name} status={status} "
                    f"output_len={len(output_str)}"
                )

                yield ToolResultEvent(
                    tool=tool_name,
                    args=tool_input if isinstance(tool_input, dict) else {"value": str(tool_input)},
                    output=output_str,
                    status=status,
                )

            elif kind == "on_chain_end" and name == "format_response":
                # Fallback: Ollama não emite on_chat_model_stream para a resposta
                # final quando há ToolMessages no contexto (limitação do tool_use).
                # Nesse caso emitimos o texto completo de uma vez.
                if not tokens_emitted:
                    output = event["data"].get("output", {})
                    response_text = output.get("response", "") if isinstance(output, dict) else ""
                    if response_text:
                        logger.info(
                            f"[agente] astream fallback via format_response "
                            f"| len={len(response_text)}"
                        )
                        yield TextChunkEvent(content=response_text)
