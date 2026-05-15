from .base import ModeConfig, _load_prompt, register

QUESTIONS_MODE = ModeConfig(
    name="questions",
    allowed_tools=["read_file", "list_directory"],
    requires_project_path=True,
    system_prompt=_load_prompt("questions"),
)

register(QUESTIONS_MODE)
