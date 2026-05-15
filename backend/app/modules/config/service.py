import json
from pathlib import Path

from app.modules.config.schemas import AppConfig

# backend/app/data/config.json — gitignored via backend/app/data/
DATA_DIR = Path(__file__).parent.parent.parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"


def load_config() -> AppConfig:
    """Carrega config.json do disco. Retorna AppConfig com valores padrão se não existir."""
    if not CONFIG_FILE.exists():
        return AppConfig()
    try:
        return AppConfig.model_validate_json(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return AppConfig()


def save_config(config: AppConfig) -> None:
    """Salva AppConfig em config.json, criando o diretório se necessário."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        config.model_dump_json(indent=2),
        encoding="utf-8",
    )


def mask_config(config: AppConfig) -> dict:
    """Retorna um dict seguro para expor ao cliente — api_key nunca vai completa."""
    data = config.model_dump()
    api_key_configured = config.api_key is not None
    data["api_key"] = "***" if api_key_configured else None
    data["api_key_configured"] = api_key_configured
    return data
