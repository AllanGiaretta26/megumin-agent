from pydantic import BaseModel, Field


class PersonalitySettings(BaseModel):
    drama_level: int = Field(default=50, ge=0, le=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    language: str = "pt-BR"


class AppConfig(BaseModel):
    project_path: str | None = None
    provider: str = "ollama"          # "ollama" | "openai_compatible"
    model_name: str = "qwen3.5:9b"
    api_base_url: str | None = None
    api_key: str | None = None        # NUNCA retornar em GET — usar mask_config
    personality: PersonalitySettings = Field(default_factory=PersonalitySettings)
