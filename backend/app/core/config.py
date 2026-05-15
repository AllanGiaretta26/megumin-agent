from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do arquivo .env.

    Equivalente ao application.properties + @ConfigurationProperties do Spring Boot.
    """

    ollama_host: str = "http://localhost:11434"
    model_name: str = "qwen3.5:9b"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Singleton — importado pelos módulos que precisam de configuração
settings = Settings()
