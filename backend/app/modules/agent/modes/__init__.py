# Importar todos os modos garante que register() seja chamado e o registry seja populado.
from . import agent_mode, autonomous_edit_mode, free_chat_mode, planning_mode, questions_mode
from .base import ModeConfig, from_name

__all__ = ["ModeConfig", "from_name"]
