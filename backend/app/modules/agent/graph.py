from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.core.exceptions import OllamaUnavailableError
from app.shared.logger import logger

from .state import AgentState


def _call_llm(state: AgentState) -> dict:
    """Nó 1: invoca o LLM com o histórico completo de mensagens.

    O LLM não tem memória própria — enviamos o histórico inteiro a cada chamada
    para simular continuidade de conversa. Sem esse envio, cada resposta seria
    gerada sem contexto das mensagens anteriores.
    """
    # ChatOllama é o adapter LangChain para o Ollama local.
    # HumanMessage / AIMessage são os tipos que ele entende — equivalem a
    # { role: "user" } e { role: "assistant" } da API do OpenAI.
    llm = ChatOllama(model=settings.model_name, base_url=settings.ollama_host)
    try:
        ai_message: AIMessage = llm.invoke(state["messages"])
        return {"response": str(ai_message.content)}
    except Exception as exc:
        logger.error(f"Erro ao invocar LLM: {exc}")
        raise OllamaUnavailableError(
            f"Ollama não está disponível em {settings.ollama_host}."
        ) from exc


def _format_response(state: AgentState) -> dict:
    """Nó 2: formata a resposta antes de devolver.

    Por enquanto é pass-through. Na Fase 7 aqui entrará o ajuste de drama_level,
    que modifica o texto da resposta conforme a personalidade configurada.
    """
    return {}


# StateGraph é uma máquina de estados — cada nó é um passo de processamento
# e as arestas definem a ordem de execução. Compilado uma única vez ao
# importar o módulo (singleton), reutilizado em todas as requisições.
_builder = StateGraph(AgentState)
_builder.add_node("call_llm", _call_llm)
_builder.add_node("format_response", _format_response)
_builder.set_entry_point("call_llm")
_builder.add_edge("call_llm", "format_response")
_builder.add_edge("format_response", END)
_graph = _builder.compile()


class AgentService:
    """Orquestra a execução do agente via LangGraph."""

    def run(self, messages: list, session_id: str) -> str:
        """Executa o grafo e retorna o texto da resposta."""
        logger.info(f"Executando grafo | session_id={session_id} | msgs={len(messages)}")
        initial_state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "response": "",
        }
        result = _graph.invoke(initial_state)
        return result["response"]
