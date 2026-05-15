import ollama

from app.core.config import settings
from app.core.exceptions import OllamaUnavailableError
from app.shared.logger import logger


class ChatService:
    """Gerencia a comunicação com o LLM via Ollama.

    Equivalente a um @Service do Spring Boot.
    """

    def __init__(self) -> None:
        self._client = ollama.Client(host=settings.ollama_host)
        self._model = settings.model_name

    def chat(self, message: str) -> str:
        """Envia uma mensagem ao LLM e retorna o texto da resposta."""
        logger.info(f"Enviando mensagem ao Ollama | model={self._model}")
        try:
            response = self._client.chat(
                model=self._model,
                messages=[{"role": "user", "content": message}],
            )
            reply: str = response.message.content
            logger.info("Ollama respondeu com sucesso")
            return reply
        except Exception as exc:
            logger.error(f"Falha na comunicação com Ollama: {exc}")
            raise OllamaUnavailableError(
                "O Ollama não está disponível. Verifique se ele está rodando em "
                f"{settings.ollama_host}."
            ) from exc
