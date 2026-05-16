import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.exceptions import ModeNotFoundError, OllamaUnavailableError
from app.modules.agent.modes import from_name as mode_from_name
from app.modules.config import load_config
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
    logger.info(f"POST /chat | mode={request.mode}")

    try:
        mode_config = mode_from_name(request.mode)
    except ModeNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if mode_config.requires_project_path and not request.project_path:
        raise HTTPException(
            status_code=400,
            detail=f"Modo '{request.mode}' requer um project_path configurado.",
        )

    service = ChatService()
    try:
        response, session_id = service.chat(
            request.message,
            request.session_id,
            request.mode,
            request.project_path,
        )
        return ChatResponse(response=response, session_id=session_id)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ModeNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Streaming de resposta token a token via Server-Sent Events (SSE).

    SSE mantém a conexão HTTP aberta e envia dados em fragmentos.
    Cada evento tem formato: "data: {json}\\n\\n"
    """
    try:
        mode_config = mode_from_name(request.mode)
    except ModeNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if mode_config.requires_project_path and not request.project_path:
        raise HTTPException(
            status_code=400,
            detail=f"Modo '{request.mode}' requer um project_path configurado.",
        )

    session_id = request.session_id or str(uuid4())
    if not memory.session_exists(session_id):
        memory.init_session(session_id)
    memory.save_message(session_id, "user", request.message)
    history = memory.get_history(session_id)
    personality = load_config().personality

    service = ChatService()

    async def generate():
        accumulated: list[str] = []
        try:
            async for token in service._agent.astream(
                messages=history,
                session_id=session_id,
                mode=request.mode,
                project_path=request.project_path or "",
                drama_level=personality.drama_level,
                language=personality.language,
            ):
                accumulated.append(token)
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            full_response = "".join(accumulated)
            memory.save_message(session_id, "assistant", full_response)
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        except Exception as exc:
            logger.error(f"[stream] Erro durante streaming: {exc}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
