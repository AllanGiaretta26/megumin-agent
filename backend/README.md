# Backend — Agent AI Megumin

API REST em FastAPI que alimenta o agente de IA Megumin.

## Pré-requisitos

| Ferramenta | Versão mínima | Instalação |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/) |
| uv | qualquer | `pip install uv` ou [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Ollama | qualquer | [ollama.com](https://ollama.com/) |

Com o Ollama instalado, baixe o modelo:

```bash
ollama pull qwen3.5:9b
```

## Instalação

```bash
cd backend

# Cria o ambiente virtual e instala todas as dependências
uv sync
```

## Configuração

```bash
cp .env.example .env
```

Edite o `.env` conforme necessário:

```env
OLLAMA_HOST=http://localhost:11434   # endereço do Ollama
MODEL_NAME=qwen3.5:9b               # modelo a usar
ENVIRONMENT=development
```

## Rodando o servidor

```bash
uv run uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

## Endpoints

### `GET /health`
Verifica se a API e o Ollama estão disponíveis.

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok", "ollama_available": true, "model": "qwen3.5:9b" }
```

---

### `POST /chat/new`
Cria uma nova sessão de conversa com memória persistente.

```bash
curl -X POST http://localhost:8000/chat/new
```

```json
{ "session_id": "27c79158-abd0-4aee-8fec-ce00c0a07bd5" }
```

---

### `POST /chat`
Envia uma mensagem ao agente. O campo `mode` define o comportamento.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "O que é recursão?",
    "mode": "study"
  }'
```

Com sessão e acesso a arquivos:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Liste os arquivos do projeto.",
    "mode": "planning",
    "session_id": "27c79158-abd0-4aee-8fec-ce00c0a07bd5",
    "project_path": "/caminho/para/seu/projeto"
  }'
```

**Modos disponíveis:**

| Modo | Acesso a arquivos | Requer `project_path` |
|---|---|---|
| `study` | Nenhum | Não |
| `questions` | Leitura | Sim |
| `planning` | Leitura | Sim |
| `agent` | Leitura + Escrita | Sim |
| `autonomous_edit` | Leitura + Escrita | Sim |

---

### `GET /chat/{session_id}/history`
Retorna o histórico de mensagens de uma sessão.

```bash
curl http://localhost:8000/chat/27c79158-abd0-4aee-8fec-ce00c0a07bd5/history
```

## Estrutura de pastas

```
backend/
├── app/
│   ├── main.py                  # bootstrap FastAPI, CORS, /health
│   ├── core/
│   │   ├── config.py            # settings via pydantic-settings (.env)
│   │   ├── exceptions.py        # exceções customizadas
│   │   └── security.py          # validação de path traversal
│   ├── modules/
│   │   ├── chat/                # endpoints, memória de sessão, schemas
│   │   └── agent/
│   │       ├── graph.py         # StateGraph (loop ReAct)
│   │       ├── state.py         # AgentState (TypedDict)
│   │       ├── modes/           # configuração dos 5 modos
│   │       ├── tools/           # read_file, list_directory, write_file
│   │       ├── providers/       # Ollama e OpenAI-compatible
│   │       └── prompts/         # system prompts por modo (.md)
│   └── shared/
│       └── logger.py            # logger singleton
├── .env.example
├── pyproject.toml
└── uv.lock
```
