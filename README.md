# Agent AI Megumin

Agente de IA para assistência em programação, com a personalidade dramática e teatral da Megumin de *Konosuba*. Projeto de bootcamp para aprender, na prática, construção de agentes de IA do zero.

## Pré-requisitos

- [Python 3.11+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) — gerenciador de pacotes Python
- [Ollama](https://ollama.com/) rodando localmente com um modelo baixado

```bash
ollama pull qwen3.5:9b
```

## Rodando o backend

```bash
cd backend

# Cria o ambiente e instala dependências
uv sync

# Copia e ajusta as variáveis de ambiente
cp .env.example .env

# Sobe o servidor
uv run uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`.

## Endpoints disponíveis

| Método | Endpoint  | Descrição                              |
|--------|-----------|----------------------------------------|
| GET    | `/health` | Status da API e disponibilidade do Ollama |
| POST   | `/chat`   | Envia uma mensagem e recebe resposta do LLM |

Exemplo de uso:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, quem é você?"}'
```

## Stack

| Camada   | Tecnologias                              |
|----------|------------------------------------------|
| Backend  | Python, FastAPI, LangGraph, LangChain    |
| Frontend | Next.js, TypeScript, Tailwind, shadcn/ui |
| LLM      | Ollama (local)                           |
