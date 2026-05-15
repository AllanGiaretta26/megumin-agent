from .base import ModeConfig, _load_prompt, register

PLANNING_MODE = ModeConfig(
    name="planning",
    allowed_tools=["read_file", "list_directory"],
    requires_project_path=True,
    system_prompt=_load_prompt("planning"),
)

register(PLANNING_MODE)
