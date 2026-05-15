import os

import ollama
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.modules.config.schemas import AppConfig
from app.modules.config.service import load_config, mask_config, save_config
from app.shared.logger import logger

router = APIRouter(tags=["config"])


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
    if body.api_key == "***":
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


@router.get("/models")
def list_models() -> dict:
    """Lista modelos instalados no Ollama."""
    logger.info("GET /models")
    try:
        client = ollama.Client(host=settings.ollama_host)
        response = client.list()
        # A API do Ollama retorna um objeto com atributo 'models' (lista de objetos Model)
        models = [m.model for m in response.models]
        return {"models": models, "ollama_available": True}
    except Exception as exc:
        logger.error(f"Ollama indisponível ao listar modelos: {exc}")
        return {"models": [], "ollama_available": False}
