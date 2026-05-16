from uuid import uuid4

from app.core.exceptions import OllamaUnavailableError
from app.modules.agent import AgentService
from app.modules.config import load_config
from app.shared.logger import logger

from . import memory


class ChatService:
    """Orquestra memória de sessão e execução do agente.

    Equivalente a um @Service do Spring Boot.
    """

    def __init__(self) -> None:
        self._agent = AgentService()

    def chat(
        self,
        message: str,
        session_id: str | None = None,
        mode: str = "study",
        project_path: str | None = None,
    ) -> tuple[str, str]:
        """Processa uma mensagem e retorna (resposta, session_id).

        Se session_id não for fornecido, cria uma sessão temporária que é
        descartada após a resposta — sem contexto entre chamadas.
        """
        is_temp = session_id is None
        if session_id is None:
            session_id = str(uuid4())

        if not memory.session_exists(session_id):
            memory.init_session(session_id)

        memory.save_message(session_id, "user", message)
        history = memory.get_history(session_id)

        logger.info(
            f"Processando mensagem | session_id={session_id} "
            f"mode={mode} | histórico={len(history)} msgs"
        )

        try:
            personality = load_config().personality
            # Tool calls e ToolMessages intermediários ficam dentro do grafo —
            # o service.py só recebe a resposta textual final.
            response = self._agent.run(
                messages=history,
                session_id=session_id,
                mode=mode,
                project_path=project_path or "",
                drama_level=personality.drama_level,
                language=personality.language,
            )
        except OllamaUnavailableError:
            memory.clear_session(session_id)
            raise

        memory.save_message(session_id, "assistant", response)

        if is_temp:
            memory.clear_session(session_id)

        return response, session_id
