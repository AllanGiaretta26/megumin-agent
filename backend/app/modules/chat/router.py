from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.core.exceptions import OllamaUnavailableError
from app.shared.logger import logger

from . import memory
from .schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageRecord,
    NewSessionResponse,
)
from .service import ChatService

router = APIRouter()


@router.post("/chat/new", response_model=NewSessionResponse)
def new_session() -> NewSessionResponse:
    """Cria uma nova sessão de conversa e retorna o session_id."""
    session_id = str(uuid4())
    memory.init_session(session_id)
    logger.info(f"Nova sessão criada | session_id={session_id}")
    return NewSessionResponse(session_id=session_id)


@router.get("/chat/{session_id}/history", response_model=HistoryResponse)
def get_history(session_id: str) -> HistoryResponse:
    """Retorna o histórico completo de mensagens de uma sessão."""
    logger.info(f"GET /chat/{session_id}/history")
    if not memory.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Sessão '{session_id}' não encontrada.")
    messages = [MessageRecord(**m) for m in memory.get_history_as_dicts(session_id)]
    return HistoryResponse(session_id=session_id, messages=messages)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Envia uma mensagem ao agente e retorna a resposta com o session_id."""
    logger.info("POST /chat")
    service = ChatService()
    try:
        response, session_id = service.chat(request.message, request.session_id)
        return ChatResponse(response=response, session_id=session_id)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
