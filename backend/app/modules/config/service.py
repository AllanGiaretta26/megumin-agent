import json
from pathlib import Path

import httpx

from app.core.exceptions import ModelListError
from app.modules.config.schemas import AppConfig
from app.shared.logger import logger

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


# Snapshot dos campos críticos da config no momento em que o backend subiu.
# Usado por GET /config/restart-required para comparar com a config no disco
# e avisar o usuário quando precisa reiniciar. Capturado uma única vez na
# primeira chamada a get_runtime_config_snapshot — depois disso é imutável
# durante o lifetime do processo.
_RUNTIME_SNAPSHOT: dict | None = None


def _build_snapshot(config: AppConfig) -> dict:
    return {
        "provider": config.provider,
        "model_name": config.model_name,
        "api_base_url": config.api_base_url,
        "api_key_configured": config.api_key is not None,
    }


def get_runtime_config_snapshot() -> dict:
    """Retorna o snapshot dos campos críticos lidos quando o backend subiu.

    Os campos comparados pelo /restart-required são apenas os que o
    AgentService cacheia no boot (provider, model, base_url, presença
    de api_key). api_key NÃO é armazenada — só o booleano de presença.
    """
    global _RUNTIME_SNAPSHOT
    if _RUNTIME_SNAPSHOT is None:
        _RUNTIME_SNAPSHOT = _build_snapshot(load_config())
    return _RUNTIME_SNAPSHOT


_OLLAMA_DEFAULT_HOST = "http://localhost:11434"


async def list_models(
    provider: str,
    api_base_url: str,
    api_key: str | None = None,
) -> list[str]:
    """Retorna lista de nomes de modelos disponíveis no provider.

    Recebe os parâmetros diretamente (não lê do disco) — assim o frontend
    pode testar valores ainda não salvos no formulário de Configurações.

    - provider="ollama": GET {base_url ou localhost:11434}/api/tags
    - provider="openai_compatible": GET {base_url}/models com Bearer auth

    Raises:
        ModelListError: falha de rede, auth ou formato inesperado.
    """
    base_url = (api_base_url or "").rstrip("/")

    if provider == "ollama":
        host = base_url or _OLLAMA_DEFAULT_HOST
        url = f"{host}/api/tags"
        headers: dict[str, str] = {}
        parse = _parse_ollama_response
    elif provider == "openai_compatible":
        if not base_url:
            raise ModelListError(
                "api_base_url é obrigatória para provider 'openai_compatible'."
            )
        if not api_key:
            raise ModelListError(
                "api_key é obrigatória para provider 'openai_compatible'."
            )
        url = f"{base_url}/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        parse = _parse_openai_response
    else:
        raise ModelListError(f"Provider desconhecido: {provider!r}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        logger.warning(f"list_models: falha de rede em {url} | {exc}")
        raise ModelListError(
            f"Não foi possível conectar ao provider em {url}."
        ) from exc

    if response.status_code == 401:
        raise ModelListError("Credenciais inválidas (401). Verifique a api_key.")
    if response.status_code == 404:
        raise ModelListError(
            f"Endpoint não encontrado em {url} (404). Verifique a api_base_url."
        )
    if response.status_code >= 400:
        raise ModelListError(
            f"Provider respondeu {response.status_code}: {response.text[:200]}"
        )

    try:
        names = parse(response.json())
    except (ValueError, KeyError, TypeError) as exc:
        raise ModelListError(
            f"Resposta inesperada do provider: {exc}"
        ) from exc

    return sorted(names)


async def list_models_from_config() -> list[str]:
    """Lê config do disco e delega para list_models().

    Usado pelo GET /models — mantém retrocompatibilidade e serve para o
    carregamento inicial da página de Configurações (sem race condition
    com o estado do formulário).
    """
    config = load_config()
    return await list_models(
        provider=config.provider,
        api_base_url=config.api_base_url or "",
        api_key=config.api_key,
    )


def _parse_ollama_response(payload: dict) -> list[str]:
    return [m["name"] for m in payload.get("models", [])]


def _parse_openai_response(payload: dict) -> list[str]:
    return [m["id"] for m in payload.get("data", [])]
