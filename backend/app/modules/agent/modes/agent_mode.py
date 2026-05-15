from .base import ModeConfig, _load_prompt, register

AGENT_MODE = ModeConfig(
    name="agent",
    allowed_tools=["read_file", "list_directory", "write_file"],
    requires_project_path=True,
    system_prompt=_load_prompt("agent"),
)

register(AGENT_MODE)
