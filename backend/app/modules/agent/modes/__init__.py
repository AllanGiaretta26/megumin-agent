# Importar todos os modos garante que register() seja chamado e o registry seja populado.
from . import agent_mode, autonomous_edit_mode, planning_mode, questions_mode, study_mode
from .base import ModeConfig, from_name

__all__ = ["ModeConfig", "from_name"]
