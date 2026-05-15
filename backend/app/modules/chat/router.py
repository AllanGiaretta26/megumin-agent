from fastapi import APIRouter, HTTPException

from app.core.exceptions import OllamaUnavailableError
from app.shared.logger import logger

from .schemas import ChatRequest, ChatResponse
from .service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Recebe uma mensagem e retorna a resposta do LLM."""
    logger.info("POST /chat")
    service = ChatService()
    try:
        reply = service.chat(request.message)
        return ChatResponse(response=reply)
    except OllamaUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
