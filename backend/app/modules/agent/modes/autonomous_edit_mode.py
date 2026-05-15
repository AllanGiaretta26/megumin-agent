from .base import ModeConfig, _load_prompt, register

AUTONOMOUS_EDIT_MODE = ModeConfig(
    name="autonomous_edit",
    allowed_tools=["read_file", "list_directory", "write_file"],
    requires_project_path=True,
    system_prompt=_load_prompt("autonomous_edit"),
)

register(AUTONOMOUS_EDIT_MODE)
