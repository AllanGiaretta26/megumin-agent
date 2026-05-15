# Agent AI Megumin

> *"Meu nome é Megumin! A maior arquimaga da Crimson Demon Clan! E minha magia... é EXPLOSÃO!!!"*

Agente de IA para assistência em programação com a personalidade dramática e teatral da Megumin de *Konosuba*. Projeto de bootcamp para aprender, na prática, construção de agentes de IA do zero — incluindo orquestração de estados (LangGraph), tool calling, streaming SSE e interface conversacional.

![Interface do Megumin Agent](docs/screenshot.png)

---

## Funcionalidades

- **5 modos operacionais** — de professor paciente a editor autônomo de código
- **Streaming token a token** — respostas em tempo real via SSE
- **Personalidade configurável** — `drama_level` de 0 (profissional) a 100 (EXPLOSÃO!!!)
- **Sandbox de arquivos** — o agente só acessa o diretório que você autorizar
- **Tool calling** — lê, lista e escreve arquivos conforme o modo ativo
- **Interface dark com tema Megumin** — roxo, vermelho e muita magia

---

## Pré-requisitos

| Requisito | Versão | Link |
|-----------|--------|------|
| Python | 3.11+ | [python.org](https://www.python.org/) |
| uv | latest | [astral.sh/uv](https://docs.astral.sh/uv/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| Ollama | latest | [ollama.com](https://ollama.com/) |

### Baixar um modelo no Ollama

```bash
ollama pull qwen3.5:9b
```

---

## Como rodar

### 1. Backend

```bash
cd backend

# Instala dependências
uv sync

# (Opcional) Copia variáveis de ambiente
cp .env.example .env

# Sobe o servidor
uv run uvicorn app.main:app --reload --port 8000
```

API disponível em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface disponível em `http://localhost:3000`.

---

## Os 5 Modos

| Modo | Acesso a Arquivos | Descrição |
|------|:-----------------:|-----------|
| **Agente** | Leitura + Escrita | Executa tarefas autonomamente, anunciando cada ação |
| **Planejamento** | Leitura | Cria planos detalhados sem modificar nada |
| **Edição Autônoma** | Leitura + Escrita | Edita código diretamente, lista alterações ao final |
| **Dúvidas** | Leitura | Responde perguntas sobre o projeto, citando arquivos |
| **Estudo** | — | Professor de programação geral, sem acesso ao projeto |

Modos com acesso a arquivos requerem um **Project Path** configurado em Configurações.

### Atalhos de teclado

| Atalho | Ação |
|--------|------|
| `Ctrl+K` | Nova conversa |
| `Ctrl+1` | Modo Agente |
| `Ctrl+2` | Modo Planejamento |
| `Ctrl+3` | Modo Edição Autônoma |
| `Ctrl+4` | Modo Dúvidas |
| `Ctrl+5` | Modo Estudo |

---

## Configuração

Acesse `/settings` na interface ou use a API:

```bash
# Ver configuração atual
curl http://localhost:8000/config

# Atualizar configuração
curl -X PUT http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/caminho/do/seu/projeto",
    "model_name": "qwen3.5:9b",
    "provider": "ollama",
    "personality": {
      "drama_level": 75,
      "temperature": 0.7,
      "language": "pt-BR"
    }
  }'
```

### Usando API externa (OpenAI-compatible)

```bash
curl -X PUT http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai_compatible",
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "sk-...",
    "model_name": "gpt-4o"
  }'
```

---

## Modelos Testados

| Modelo | Tipo | Ferramentas | Personalidade |
|--------|------|-------------|---------------|
| qwen3.5:9b | Ollama local | ✅ Funciona | ⚠️ Parcial |
| llama3.1:8b | Ollama local | ✅ Funciona | ❌ Ignora persona |
| gemma4:e4b | Ollama local | ✅ Funciona | ❌ Ignora persona |

**Observação:** modelos locais pequenos (abaixo de 13B) tendem a ignorar instruções de roleplay via system prompt. As ferramentas (`read_file`, `write_file`, `list_directory`) funcionam corretamente em todos os modelos testados. Para a personalidade Megumin funcionar plenamente, recomenda-se usar modelos maiores via Ollama ou APIs externas como OpenRouter ou Gemini.

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status da API e Ollama |
| POST | `/chat/new` | Cria nova sessão |
| POST | `/chat` | Envia mensagem (resposta completa) |
| POST | `/chat/stream` | Envia mensagem (streaming SSE) |
| GET | `/chat/{id}/history` | Histórico da sessão |
| GET | `/config` | Configuração atual (api_key mascarada) |
| PUT | `/config` | Atualiza configuração |
| POST | `/config/validate-path` | Valida um diretório |
| GET | `/models` | Lista modelos Ollama instalados |

---

## Estrutura do Projeto

```
megumin-agent/
├── backend/
│   └── app/
│       ├── main.py              # Bootstrap FastAPI
│       ├── core/                # Settings, exceptions, sandbox de path
│       ├── modules/
│       │   ├── agent/           # LangGraph StateGraph, 5 modos, tools, providers
│       │   ├── chat/            # Sessões, memória, router de chat
│       │   └── config/          # Configuração persistida em JSON
│       └── shared/              # Logger, tipos globais
│
└── frontend/
    └── src/
        ├── app/                 # Rotas Next.js (/, /settings)
        ├── components/layout/   # Sidebar, ChatLayout
        └── features/
            ├── chat/            # Hook useChat, componentes de mensagem, API
            ├── config/          # Hook useConfig, formulário de settings
            └── modes/           # Definição dos 5 modos
```

---

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Backend | Python 3.11+, FastAPI, LangGraph, LangChain, langchain-ollama |
| Frontend | Next.js 16, TypeScript, Tailwind CSS v4, shadcn/ui, react-markdown |
| LLM local | Ollama |
| LLM externo | Qualquer API OpenAI-compatible |
