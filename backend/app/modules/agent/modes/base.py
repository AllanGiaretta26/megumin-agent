"""Sistema de modos operacionais do agente.

Cada modo define um comportamento distinto usando o padrão Strategy:
a interface externa (ModeConfig) é sempre a mesma, mas cada modo
configura allowed_tools e system_prompt de forma diferente.

Em Java seria: interface Mode { List<String> getAllowedTools(); String getSystemPrompt(); }
com implementações AgentMode, PlanningMode, StudyMode, etc.
"""
from dataclasses import dataclass
from pathlib import Path

from app.core.exceptions import ModeNotFoundError


def _load_prompt(mode_name: str) -> str:
    """Carrega o system prompt do arquivo .md correspondente ao modo."""
    prompt_path = Path(__file__).parent.parent / "prompts" / f"{mode_name}.md"
    return prompt_path.read_text(encoding="utf-8").strip()


@dataclass(frozen=True)
class ModeConfig:
    """Configuração imutável de um modo operacional.

    frozen=True equivale a um record imutável do Java — evita modificações acidentais
    após a inicialização, importante já que as instâncias são singletons de módulo.
    """

    name: str
    allowed_tools: list[str]
    requires_project_path: bool
    system_prompt: str


# Registry: mapeia nome de modo → ModeConfig. Populado pelos módulos de modo.
_REGISTRY: dict[str, ModeConfig] = {}


def register(config: ModeConfig) -> None:
    """Registra um modo no registry global. Chamado pelos módulos de modo."""
    _REGISTRY[config.name] = config


def from_name(name: str) -> ModeConfig:
    """Retorna a configuração do modo pelo nome.

    Raises:
        ModeNotFoundError: Se o nome não estiver registrado.
    """
    if name not in _REGISTRY:
        valid = list(_REGISTRY.keys())
        raise ModeNotFoundError(
            f"Modo '{name}' não encontrado. Modos disponíveis: {valid}"
        )
    return _REGISTRY[name]


# Expõe _load_prompt para os módulos de modo sem importação circular
__all__ = ["ModeConfig", "register", "from_name", "_load_prompt"]
