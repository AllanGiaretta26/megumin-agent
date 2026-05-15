from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # None = sem sessão / conversa sem contexto


class ChatResponse(BaseModel):
    response: str
    session_id: str  # sempre retornado, mesmo que gerado internamente


class NewSessionResponse(BaseModel):
    session_id: str


class MessageRecord(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageRecord]
