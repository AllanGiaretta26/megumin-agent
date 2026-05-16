from langchain_openai import ChatOpenAI

from .base import BaseLLMProvider


class OpenAICompatProvider(BaseLLMProvider):
    """Provider para APIs compatíveis com OpenAI (qualquer endpoint OpenAI-like)."""

    def __init__(
        self,
        model_name: str,
        base_url: str | None,
        api_key: str,
        temperature: float,
    ) -> None:
        self._model_name = model_name
        self._base_url = base_url
        self._api_key = api_key
        self._temperature = temperature

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self._model_name,
            base_url=self._base_url,
            api_key=self._api_key,
            temperature=self._temperature,
        )
