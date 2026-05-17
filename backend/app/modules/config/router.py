import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.exceptions import ModelListError
from app.modules.config.schemas import AppConfig
from app.modules.config.service import (
    get_runtime_config_snapshot,
    list_models,
    list_models_from_config,
    load_config,
    mask_config,
    save_config,
)
from app.shared.logger import logger

router = APIRouter(tags=["config"])

# Sentinel usado para indicar "manter a api_key salva no disco" — tanto no
# PUT /config quanto no POST /models. O GET /config devolve "***" em vez da
# chave real (mascaramento), e o frontend pode reenviar esse mesmo valor.
API_KEY_SENTINEL = "***"


@router.get("/config")
def get_config() -> dict:
    """Retorna a configuração atual com api_key mascarada."""
    logger.info("GET /config")
    return mask_config(load_config())


@router.put("/config")
def update_config(body: AppConfig) -> dict:
    """Atualiza a configuração. Se api_key vier como '***', mantém o valor atual."""
    logger.info("PUT /config")

    current = load_config()

    # Preserva a chave real se o cliente enviou o placeholder mascarado
    if body.api_key == API_KEY_SENTINEL:
        body = body.model_copy(update={"api_key": current.api_key})

    # Valida project_path se fornecido
    if body.project_path is not None:
        if not os.path.isdir(body.project_path):
            raise HTTPException(
                status_code=422,
                detail=f"project_path inválido: '{body.project_path}' não é um diretório existente.",
            )

    save_config(body)
    return mask_config(body)


class ValidatePathRequest(BaseModel):
    path: str


@router.post("/config/validate-path")
def validate_path(body: ValidatePathRequest) -> dict:
    """Verifica se um caminho existe, é diretório e tem permissão de leitura."""
    logger.info(f"POST /config/validate-path — path={body.path!r}")

    if not os.path.isdir(body.path):
        return {"valid": False, "error": "Caminho não existe ou não é um diretório."}

    if not os.access(body.path, os.R_OK):
        return {"valid": False, "error": "Sem permissão de leitura neste diretório."}

    return {"valid": True, "error": None}


@router.get("/config/restart-required")
def restart_required() -> dict:
    """Compara config no disco com snapshot do boot.

    Retorna quais campos críticos divergem — o frontend usa pra mostrar
    banner de "reinicie o backend pra aplicar".
    """
    logger.info("GET /config/restart-required")
    current = load_config()
    snapshot = get_runtime_config_snapshot()

    comparisons = {
        "provider": (snapshot["provider"], current.provider),
        "model_name": (snapshot["model_name"], current.model_name),
        "api_base_url": (snapshot["api_base_url"], current.api_base_url),
        "api_key": (snapshot["api_key_configured"], current.api_key is not None),
    }
    changed = [k for k, (snap, now) in comparisons.items() if snap != now]
    return {"restart_required": bool(changed), "changed_fields": changed}


@router.get("/models")
async def get_models() -> dict:
    """Lista modelos disponíveis no provider atualmente configurado (lê do disco)."""
    logger.info("GET /models")
    try:
        models = await list_models_from_config()
        return {"models": models}
    except ModelListError as exc:
        logger.warning(f"GET /models falhou: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))


class ListModelsRequest(BaseModel):
    provider: str
    api_base_url: str
    api_key: str | None = None  # opcional para provider="ollama"


@router.post("/models")
async def list_models_endpoint(req: ListModelsRequest) -> dict:
    """Lista modelos usando os parâmetros do request (sem ler do disco).

    Útil para o frontend testar valores ainda não salvos no formulário —
    evita race condition em que provider novo é combinado com base_url
    antiga do disco.

    Se api_key vier como API_KEY_SENTINEL ("***"), substitui pela chave
    salva no disco antes de chamar o provider — assim o frontend não
    precisa conhecer a chave real (que nunca sai do GET /config).
    """
    logger.info(f"POST /models — provider={req.provider}")

    api_key = req.api_key
    if api_key == API_KEY_SENTINEL:
        saved_key = load_config().api_key
        if not saved_key:
            raise HTTPException(
                status_code=400,
                detail=(
                    "API key não configurada. Envie uma chave válida ou "
                    "salve uma primeiro."
                ),
            )
        api_key = saved_key

    try:
        models = await list_models(
            provider=req.provider,
            api_base_url=req.api_base_url,
            api_key=api_key,
        )
        return {"models": models}
    except ModelListError as exc:
        logger.warning(f"POST /models falhou: {exc}")
        raise HTTPException(status_code=502, detail=str(exc))
