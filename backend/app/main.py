import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.chat import router as chat_router
from app.modules.config import router as config_router
from app.shared.logger import logger

app = FastAPI(title="Agent AI Megumin", version="0.1.0")

# Equivalente à configuração de CORS no Spring Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(config_router)


@app.get("/health")
def health_check() -> dict[str, object]:
    """Verifica se a API e o Ollama estão disponíveis."""
    logger.info("GET /health")

    try:
        client = ollama.Client(host=settings.ollama_host)
        client.list()
        ollama_available = True
    except Exception as exc:
        logger.error(f"Ollama indisponível no health check: {exc}")
        ollama_available = False

    return {
        "status": "ok",
        "ollama_available": ollama_available,
        "model": settings.model_name,
    }
