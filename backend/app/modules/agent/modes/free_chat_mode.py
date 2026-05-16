from .base import ModeConfig, _load_prompt, register

FREE_CHAT_MODE = ModeConfig(
    name="free_chat",
    allowed_tools=[],
    requires_project_path=False,
    system_prompt=_load_prompt("free_chat"),
)

register(FREE_CHAT_MODE)
