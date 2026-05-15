from .base import ModeConfig, _load_prompt, register

STUDY_MODE = ModeConfig(
    name="study",
    allowed_tools=[],
    requires_project_path=False,
    system_prompt=_load_prompt("study"),
)

register(STUDY_MODE)
