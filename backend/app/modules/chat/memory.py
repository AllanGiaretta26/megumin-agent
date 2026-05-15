from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

# Armazenamento em memória RAM: session_id → lista de mensagens LangChain.
# Intencional — persistência real em disco/banco está fora do escopo do bootcamp
# (ver seção 7.2 do briefing). Os dados são perdidos ao reiniciar o servidor.
_sessions: dict[str, list[BaseMessage]] = {}


def session_exists(session_id: str) -> bool:
    return session_id in _sessions


def init_session(session_id: str) -> None:
    _sessions[session_id] = []


def get_history(session_id: str) -> list[BaseMessage]:
    return _sessions.get(session_id, [])


def save_message(session_id: str, role: str, content: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    msg: BaseMessage = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
    _sessions[session_id].append(msg)


def get_history_as_dicts(session_id: str) -> list[dict[str, str]]:
    """Retorna o histórico serializado para respostas da API."""
    return [
        {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": str(m.content)}
        for m in _sessions.get(session_id, [])
    ]


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
