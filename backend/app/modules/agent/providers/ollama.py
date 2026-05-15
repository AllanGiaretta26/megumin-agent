from langchain_ollama import ChatOllama

from app.core.config import settings

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider para modelos rodando localmente via Ollama."""

    def get_llm(self) -> ChatOllama:
        return ChatOllama(model=settings.model_name, base_url=settings.ollama_host)
