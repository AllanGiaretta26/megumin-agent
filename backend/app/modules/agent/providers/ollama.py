from langchain_ollama import ChatOllama

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider para modelos rodando localmente via Ollama."""

    def __init__(self, model_name: str, base_url: str | None, temperature: float) -> None:
        self._model_name = model_name
        self._base_url = base_url
        self._temperature = temperature

    def get_llm(self) -> ChatOllama:
        return ChatOllama(
            model=self._model_name,
            base_url=self._base_url,
            temperature=self._temperature,
        )
