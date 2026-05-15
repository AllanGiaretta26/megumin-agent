from langchain_openai import ChatOpenAI

from app.core.config import settings

from .base import BaseLLMProvider


class OpenAICompatProvider(BaseLLMProvider):
    """Provider para APIs compatíveis com OpenAI (qualquer endpoint OpenAI-like).

    Placeholder funcional — base_url e api_key serão configuráveis
    pela tela de settings na Fase 6.
    """

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=settings.model_name,
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key or "placeholder",
        )
