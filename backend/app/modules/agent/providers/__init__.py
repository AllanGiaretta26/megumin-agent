from app.modules.config.schemas import AppConfig

from .base import BaseLLMProvider
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider


def build_provider(config: AppConfig) -> BaseLLMProvider:
    """Constrói o provider de LLM apropriado a partir da config do app.

    Lê provider, model_name, api_base_url, api_key e
    personality.temperature da config.
    """
    provider_name = config.provider
    temperature = config.personality.temperature

    if provider_name == "ollama":
        return OllamaProvider(
            model_name=config.model_name,
            base_url=config.api_base_url,
            temperature=temperature,
        )
    if provider_name == "openai_compatible":
        if not config.api_key:
            raise ValueError(
                "api_key obrigatória para provider openai_compatible"
            )
        return OpenAICompatProvider(
            model_name=config.model_name,
            base_url=config.api_base_url,
            api_key=config.api_key,
            temperature=temperature,
        )
    raise ValueError(f"Provider desconhecido: {provider_name!r}")


__all__ = [
    "BaseLLMProvider",
    "OllamaProvider",
    "OpenAICompatProvider",
    "build_provider",
]
