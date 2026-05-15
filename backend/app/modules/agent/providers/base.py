from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool


class BaseLLMProvider(ABC):
    """Interface comum para providers de LLM.

    Equivalente a uma interface Java — garante que qualquer provider
    (Ollama, OpenAI, etc.) exponha os mesmos métodos para o grafo.
    """

    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        """Retorna a instância do LLM sem tools vinculadas."""

    def get_llm_with_tools(self, tools: list[BaseTool]) -> BaseChatModel:
        """Retorna o LLM com as tools vinculadas via bind_tools.

        bind_tools insere os schemas das tools no prompt do sistema do LLM,
        permitindo que ele gere tool_calls quando julgar necessário.
        """
        return self.get_llm().bind_tools(tools)
