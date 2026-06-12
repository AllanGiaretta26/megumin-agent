# 🎆 Briefing — Agent AI Megumin

> **Documento de contexto do projeto.**
> Este arquivo é a fonte da verdade sobre escopo, decisões técnicas e estado atual.
> Sempre consulte-o antes de tomar decisões de implementação.

---

## 📚 Índice

1. [Visão Geral](#1-visão-geral)
2. [Funcionalidades Principais](#2-funcionalidades-principais)
3. [Stack Técnica](#3-stack-técnica)
4. [Arquitetura](#4-arquitetura)
5. [Regras de Modularização](#5-regras-de-modularização)
6. [Plano de Execução](#6-plano-de-execução-7-fases)
7. [Regras e Restrições](#7-regras-e-restrições)
8. [Convenções de Código](#8-convenções-de-código)
9. [Convenções de Personalidade](#9-convenções-de-personalidade)
10. [Endpoints da API](#10-endpoints-da-api-referência-rápida)
11. [Glossário](#11-glossário-rápido)
12. [Próximos Passos](#12-próximos-passos-pós-bootcamp)
13. [Observações para o Claude Code](#-observações-finais-para-o-claude-code)

---

## 1. Visão Geral

**Nome:** Agent AI Megumin

**Tipo:** Agente de IA para assistência em programação

**Inspiração:** Personagem Megumin (anime/light novel *Konosuba*) — uma maga arquimaga obcecada por magia de explosão. A personalidade do agente é **dramática, explosiva e teatral**, mas mantém competência técnica real.

**Objetivo do projeto:** Projeto de bootcamp para aprender, na prática, como construir agentes de IA do zero — incluindo orquestração de estados, integração com LLMs locais, tool calling e interface conversacional.

**Nível do desenvolvedor:** Júnior — vindo de Java/Spring Boot, aprendendo Python, agentes de IA e frontend moderno simultaneamente.

---

## 2. Funcionalidades Principais

### 2.1 Cinco Modos Operacionais

O agente opera em **um modo por vez**, definido pelo usuário antes de cada interação:

| Modo | Descrição | Pode escrever arquivos? | Precisa de `project_path`? |
|------|-----------|------------------------|----------------------------|
| **Agente** | Executa tarefas autonomamente, anunciando ações antes de cada escrita | ✅ Sim | ✅ Sim |
| **Planejamento** | Cria um plano detalhado antes de qualquer execução. Só lê, não escreve | ❌ Não | ✅ Sim |
| **Edição Autônoma** | Edita código diretamente, sem anunciar. Lista alterações no final | ✅ Sim | ✅ Sim |
| **Dúvidas** | Responde perguntas sobre o projeto atual, sempre citando arquivos consultados | ❌ Não | ✅ Sim |
| **Estudo** | Modo "professor". Responde dúvidas gerais de programação fora do contexto do projeto | ❌ Não | ❌ Não |

> ℹ️ **Nota sobre "confirmação" no Modo Agente:** como a API é REST stateless, "confirmar" significa que o agente **anuncia textualmente** o que vai fazer antes de chamar a tool de escrita. Aprovação interativa (cliente envia "ok") só será implementada na Fase 7, se houver tempo.

### 2.2 Interface

- **Chat principal** com histórico de conversa
- **Sidebar** para seleção de modo e acesso a configurações
- **Tela de configurações** para:
  - Seletor de diretório de código (`project_path`)
  - Escolha entre Ollama (local) ou API externa (OpenAI-compatible)
  - Ajuste de personalidade (`drama_level`, `temperature`)
  - Idioma de resposta

### 2.3 Personalidade Configurável

O nível de drama vai de **0 a 100**:

- **0** — Respostas objetivas e profissionais (sem traços da personagem)
- **50** — Equilíbrio entre técnico e teatral
- **100** — "EXPLOSÃO!!!" — máximo drama, monólogos, bordões temáticos

> ⚠️ **Regra inquebrável:** a personalidade **nunca** pode comprometer a correção técnica do código gerado. Drama no texto, precisão no código.

---

## 3. Stack Técnica

### 3.1 Backend

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| **Python** | 3.11+ | Linguagem base |
| **uv** | Latest | Gerenciador de pacotes/ambientes |
| **FastAPI** | Latest | Framework web (API REST) |
| **Pydantic** | v2+ | Validação de dados e settings |
| **Uvicorn** | Latest | Servidor ASGI |
| **LangGraph** | Latest | Orquestração do agente (StateGraph) |
| **LangChain** | Latest | Abstrações para LLMs |
| **langchain-ollama** | Latest | Integração com Ollama |

### 3.2 Frontend

| Tecnologia | Versão | Função |
|-----------|--------|--------|
| **Next.js** | 14+ (App Router) | Framework React |
| **TypeScript** | 5+ | Tipagem estática |
| **Tailwind CSS** | 3+ | Estilização utilitária |
| **shadcn/ui** | Latest | Componentes copiáveis |
| **lucide-react** | Latest | Ícones |

### 3.3 LLMs

- **Padrão:** Ollama rodando localmente
- **Modelos recomendados:** `llama3.2:3b` (leve), `qwen2.5:7b` (médio)
- **Alternativa:** qualquer API OpenAI-compatible (configurável)

### 3.4 Justificativas das Escolhas

- **Python em vez de Java:** o ecossistema de IA (LangChain, LangGraph, Ollama) é nativamente Python. Forçar Java aqui aumentaria o atrito sem ganho pedagógico.
- **FastAPI:** sintaxe próxima ao Spring Boot (decorators, injeção, validação) — facilita transição para quem vem do Java.
- **LangGraph em vez de LangChain puro:** força a pensar o agente como grafo de estados, o que é mais didático.
- **Next.js + Tailwind + shadcn/ui:** stack que entrega o máximo pronto, reduzindo fricção no frontend (área mais fraca do dev).
- **Ollama:** roda local, gratuito, sem cartão de crédito — ideal para bootcamp.

---

## 4. Arquitetura

### 4.1 Decisão arquitetural

O projeto usa **arquitetura modular** (organização por features), com uma camada compartilhada (`core/`) para infraestrutura crítica e outra (`shared/`) para utilitários neutros.

**Por que modular e não em camadas planas:**

1. Os 3 contextos (`chat`, `config`, `agent`) têm responsabilidades muito distintas
2. Critério explícito do projeto: "reaproveitamento em outros projetos pessoais"
3. Modularização é base para conceitos futuros (Hexagonal, Clean, DDD)
4. Onboarding mais rápido — toda lógica de uma feature está numa pasta só

**Por que NÃO microsserviços:** complexidade desproporcional ao escopo. Um monolito modular bem feito atende tudo que precisamos.

### 4.2 Diagrama de sistema

```
┌────────────────────────────────────────────────────────────┐
│                       BROWSER                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            FRONTEND (Next.js)                        │  │
│  │  app/  ←  features/  ←  components/  ←  lib/         │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────┘
                            │ HTTP (REST + SSE)
                            ▼
┌────────────────────────────────────────────────────────────┐
│                     LOCALHOST:8000                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            BACKEND (FastAPI)                         │  │
│  │                                                      │  │
│  │   modules/chat/   modules/config/   modules/agent/   │  │
│  │           ↓             ↓                ↓           │  │
│  │              core/   (segurança, settings)           │  │
│  │              shared/ (logger, types)                 │  │
│  └─────┬────────────────────────────────────────────────┘  │
└────────┼───────────────────────────────────────────────────┘
         ▼
   ┌──────────┐       ┌──────────────┐
   │  Ollama  │       │  Filesystem  │
   │  :11434  │       │  (sandbox)   │
   └──────────┘       └──────────────┘
```

### 4.3 Estrutura de pastas — Backend

```
backend/
├── app/
│   ├── main.py                    # bootstrap FastAPI
│   │
│   ├── core/                      # infraestrutura crítica compartilhada
│   │   ├── __init__.py
│   │   ├── config.py              # settings via Pydantic
│   │   ├── exceptions.py          # exceptions customizadas
│   │   └── security.py            # validação de paths, sandbox
│   │
│   ├── modules/                   # módulos por feature
│   │   │
│   │   ├── chat/
│   │   │   ├── __init__.py        # expõe interface pública
│   │   │   ├── router.py          # endpoints /chat/*
│   │   │   ├── service.py         # lógica de chat
│   │   │   ├── schemas.py         # ChatRequest, ChatResponse
│   │   │   └── memory.py          # gerenciamento de sessões
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # endpoints /config/*
│   │   │   ├── service.py         # carrega/salva config.json
│   │   │   └── schemas.py         # AppConfig, Personality
│   │   │
│   │   └── agent/
│   │       ├── __init__.py
│   │       ├── graph.py           # StateGraph principal
│   │       ├── state.py           # TypedDict do estado
│   │       │
│   │       ├── modes/             # 1 arquivo por modo
│   │       │   ├── base.py        # BaseMode (interface)
│   │       │   ├── agent_mode.py
│   │       │   ├── planning_mode.py
│   │       │   ├── autonomous_edit_mode.py
│   │       │   ├── questions_mode.py
│   │       │   └── study_mode.py
│   │       │
│   │       ├── tools/             # ferramentas do agente
│   │       │   ├── base.py
│   │       │   ├── read_file.py
│   │       │   ├── list_directory.py
│   │       │   └── write_file.py
│   │       │
│   │       ├── prompts/           # system prompts (.md)
│   │       │   ├── agent.md
│   │       │   ├── planning.md
│   │       │   ├── autonomous_edit.md
│   │       │   ├── questions.md
│   │       │   └── study.md
│   │       │
│   │       └── providers/         # adapters de LLM
│   │           ├── base.py        # LLMProvider (interface)
│   │           ├── ollama.py
│   │           └── openai_compat.py
│   │
│   ├── shared/                    # utilitários neutros
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── types.py
│   │
│   └── data/                      # persistência local (gitignored)
│       └── config.json
│
├── pyproject.toml
├── .env.example
└── .python-version
```

### 4.4 Estrutura de pastas — Frontend

```
frontend/
├── app/                           # rotas Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx                   # / (chat principal)
│   └── settings/
│       └── page.tsx               # /settings
│
├── features/                      # módulos por feature (espelha o backend)
│   ├── chat/
│   │   ├── components/            # ChatMessage, ChatInput, ChatContainer
│   │   ├── hooks/                 # useChat, useStream
│   │   ├── api.ts                 # chamadas aos endpoints /chat/*
│   │   └── types.ts
│   │
│   ├── config/
│   │   ├── components/            # SettingsForm, PathPicker
│   │   ├── hooks/                 # useConfig
│   │   ├── api.ts
│   │   └── types.ts
│   │
│   └── modes/
│       ├── components/            # ModeSelector
│       ├── constants.ts           # lista dos 5 modos
│       └── types.ts
│
├── components/
│   ├── ui/                        # shadcn/ui (gerado)
│   └── layout/                    # Sidebar, Header (globais)
│
├── lib/                           # utilitários puros
│   ├── api-client.ts              # cliente HTTP genérico
│   └── utils.ts                   # cn(), formatters
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── .env.local.example
```

### 4.5 Diagrama de dependências entre módulos

```
┌─────────────────────────────────────────────┐
│        APP / MAIN (entry point)             │
└─────────────────────────────────────────────┘
              │           │           │
              ▼           ▼           ▼
       ┌─────────┐  ┌─────────┐  ┌─────────┐
       │  chat   │  │ config  │  │  agent  │
       └────┬────┘  └────┬────┘  └────┬────┘
            │            │            │
            └────────────┼────────────┘
                         ▼
                ┌─────────────────┐
                │  core / shared  │
                └─────────────────┘

Regras de dependência:
✅ Módulos podem usar core e shared
✅ chat pode usar agent (via interface pública)
❌ agent NÃO pode usar chat (inversão de dependência)
❌ core/shared NÃO podem importar nada de modules
```

---

## 5. Regras de Modularização

Estas são as **4 regras de ouro** para manter a arquitetura modular saudável. Quebrar qualquer uma delas é dívida técnica.

### Regra 1: Comunicação só pela "porta da frente"

Cada módulo expõe sua interface pública via `__init__.py`. Nunca importar diretamente arquivos internos de outro módulo.

```python
# ❌ ERRADO — invade a "cozinha" do módulo chat
from app.modules.chat.memory import _internal_function

# ✅ CERTO — usa a interface exposta
from app.modules.chat import ChatService
```

**Como aplicar:** o `__init__.py` de cada módulo lista explicitamente o que é público:

```python
# app/modules/chat/__init__.py
from .service import ChatService
from .schemas import ChatRequest, ChatResponse

__all__ = ["ChatService", "ChatRequest", "ChatResponse"]
```

### Regra 2: Dependências fluem em uma direção só

```
router  →  service  →  módulos auxiliares  →  core/shared
```

Nunca o contrário. Se dois módulos parecem precisar um do outro, é sinal de que **um terceiro módulo** deveria existir.

### Regra 3: Rule of Three antes de abstrair

Código duplicado **2 vezes**: tolere. Código duplicado **3 vezes**: extraia para `shared/`.

> Evita o **DRY prematuro** — abstrair cedo demais cria acoplamento desnecessário e amarra decisões antes de ter contexto suficiente.

### Regra 4: `core/` ≠ `shared/`

| Pasta | Quando usar | Exemplos |
|-------|-------------|----------|
| **`core/`** | Infraestrutura **crítica** que define como o app funciona | settings, exceptions, security |
| **`shared/`** | Utilitários **neutros**, que poderiam estar numa lib externa | logger, formatters, types globais |

Se você está em dúvida, pergunte: "isso é específico do meu app, ou seria útil em qualquer projeto?". Específico vai para `core/`, genérico vai para `shared/`.

---

## 6. Plano de Execução (7 Fases)

| Fase | Nome | Duração estimada | Entregável |
|------|------|------------------|------------|
| 1 | Fundação: Ambiente + Ollama | 1 dia | Ollama rodando, projeto inicializado |
| 2 | Backend Base com FastAPI | 2 dias | API `/chat` simples funcionando |
| 3 | Primeiro Agente com LangGraph | 2-3 dias | Agente com memória de conversa |
| 4 | Os 5 Modos do Megumin | 3 dias | Modos funcionais com ferramentas |
| 5 | Frontend Base: Chat | 2-3 dias | Interface conversacional completa |
| 6 | Configurações + File System | 2 dias | Tela de settings, seletor de diretório |
| 7 | Personalidade, Streaming, Refino | 2 dias | Megumin "viva", respostas em streaming |

**Estado atual:** ✅ Projeto concluído — 15/05/2026

- [x] Fase 1 — Fundação
- [x] Fase 2 — Backend base
- [x] Fase 3 — Agente LangGraph
- [x] Fase 4 — Cinco modos
- [x] Fase 5 — Frontend base
- [x] Fase 6 — Configurações
- [x] Fase 7 — Refino final

### Observações pós-conclusão

- **Personalidade Megumin:** o código de injeção está correto e funcional. A limitação está nos modelos locais pequenos (qwen3.5:9b, llama3.1:8b, gemma4:e4b) que tendem a ignorar instruções de roleplay via system prompt. Para a personalidade funcionar plenamente, recomenda-se usar modelos maiores (13B+) ou APIs externas (OpenRouter, Gemini).
- **Streaming com tools:** resolvido via fallback `on_chain_end + format_response` — limitação conhecida do Ollama ao fazer streaming após execução de ferramentas.
- **Anúncio antes de escrever (Modo Agente):** comportamento dependente do modelo — modelos maiores seguem melhor essa instrução do system prompt.

---

## 7. Regras e Restrições

### 7.1 Segurança (não-negociável)

- **Sandbox de arquivos:** nenhuma ferramenta pode acessar arquivos fora de `project_path`. Sempre validar contra **path traversal** (`../`, paths absolutos suspeitos).
- **API keys:** nunca retornar a chave completa em endpoints `GET`. Mascarar no frontend (`***`).
- **`config.json`:** sempre no `.gitignore`. Nunca versionar credenciais.
- **CORS:** restrito a `http://localhost:3000` em desenvolvimento.

### 7.2 Escopo (o que **NÃO** está incluído)

Para manter o projeto focado e finalizável:

- ❌ Autenticação de usuários (projeto é local, single-user)
- ❌ Banco de dados (persistência via JSON é suficiente)
- ❌ Multi-agente (um Megumin por vez)
- ❌ RAG / embeddings (pode ser projeto seguinte)
- ❌ Deploy em produção (foco é rodar localmente)
- ❌ Testes automatizados completos (alguns testes pontuais nas tools de segurança são bem-vindos)

---

## 8. Convenções de Código

### 8.1 Nomenclatura

| Contexto | Convenção | Exemplo |
|----------|-----------|---------|
| Arquivos Python | `snake_case.py` | `chat_service.py` |
| Classes Python | `PascalCase` | `ChatService` |
| Funções/variáveis Python | `snake_case` | `def get_history()` |
| Constantes Python | `UPPER_SNAKE_CASE` | `MAX_TOKENS = 4096` |
| Arquivos TypeScript | `kebab-case.tsx` | `chat-message.tsx` |
| Componentes React | `PascalCase` | `ChatMessage` |
| Funções/variáveis TS | `camelCase` | `function sendMessage()` |
| Hooks React | `useXxx` (camelCase) | `useChat`, `useStream` |
| Endpoints HTTP | `kebab-case` em URL | `POST /chat/new-session` |
| Campos JSON | `snake_case` | `{ "session_id": "..." }` |

> 💡 **Decisão consciente:** mantemos `snake_case` no JSON da API mesmo no frontend TypeScript. Isso evita serializadores no meio do caminho. O TypeScript declara os tipos com `snake_case` quando refletindo a API, e converte para `camelCase` só se o componente precisar.

### 8.2 Qualidade de código

- **Backend:** type hints obrigatórios em todas as funções públicas. Docstrings em módulos e funções complexas.
- **Frontend:** TypeScript estrito (`strict: true`). Sem `any` exceto com comentário justificando.

### 8.3 Comentários: quando e quanto

Critério de calibração (importante — o dev é júnior mas não é iniciante):

- ✅ **Comentar:** o "porquê" de uma decisão não óbvia (ex: "usamos lock aqui porque...")
- ✅ **Comentar:** conceitos novos do ecossistema IA (TypedDict, StateGraph, etc) na primeira aparição
- ✅ **Comentar:** paralelos com Spring Boot quando agregam (ex: "# equivalente a @Service")
- ❌ **NÃO comentar:** o que o código óbvio já diz (`# incrementa contador` num `counter += 1`)
- ❌ **NÃO comentar:** sintaxe básica de Python ou TypeScript

> Regra prática: se removendo o comentário a leitura ficar mais difícil, ele deve ficar. Se ficar igual, ele sobra.

### 8.4 Logging

- Usar `app/shared/logger.py` (wrapper sobre `logging` padrão do Python)
- **Nível INFO:** eventos importantes do ciclo de vida (request recebido, modo selecionado, tool chamada)
- **Nível DEBUG:** payloads completos, estado do grafo
- **Nível ERROR:** sempre que uma exception for capturada
- Nunca logar `api_key` ou conteúdo sensível

---

## 9. Convenções de Personalidade

Quando o Megumin gerar texto, seguir estas diretrizes:

### 9.1 Bordões e referências

- Pode usar termos como "EXPLOSÃO", "Crimson Demon", "arcanos", "feitiçaria"
- Pode encerrar respostas com frases dramáticas
- Pode reclamar de "magia menos potente" (ex: código mal estruturado)

### 9.2 Limites

- **Modo Estudo:** mantém personalidade, mas a clareza didática vem primeiro
- **Modo Planejamento:** drama na introdução/conclusão, mas o plano em si é objetivo (lista numerada limpa)
- **Código gerado:** sempre tecnicamente correto, sem comentários teatrais que atrapalhem leitura
- **Mensagens de erro:** dramáticas mas informativas — o usuário precisa saber o que deu errado

### 9.3 Exemplo de calibração por `drama_level`

```
drama_level = 0   → "Função criada. Retorna x*2."
drama_level = 50  → "Pronto! Forjei a função que retorna x*2."
drama_level = 100 → "AH HA HA! Contemple minha criação arcana! Esta
                    função canaliza a essência da matemática e devolve
                    o DOBRO de x! EXPLOSÃO!!!"
```

---

## 10. Endpoints da API (referência rápida)

| Método | Endpoint | Função | Fase |
|--------|----------|--------|------|
| GET | `/health` | Health check + modelo ativo | 2 |
| POST | `/chat` | Envia mensagem (resposta completa) | 2 |
| POST | `/chat/new` | Cria nova sessão de conversa | 3 |
| GET | `/chat/{session_id}/history` | Retorna histórico da sessão | 3 |
| GET | `/models` | Lista modelos Ollama disponíveis | 6 |
| GET | `/config` | Retorna config atual (mascarando segredos) | 6 |
| PUT | `/config` | Atualiza configuração | 6 |
| POST | `/config/validate-path` | Valida se um caminho é utilizável | 6 |
| POST | `/chat/stream` | Envia mensagem (resposta em SSE) | 7 |

> A coluna **Fase** indica em qual fase do plano cada endpoint deve existir. Endpoints fora da fase atual não devem ser implementados antecipadamente.

---

## 11. Glossário Rápido

Termos que aparecem no projeto e podem ser novos para devs vindos do mundo Java:

- **LLM** — Large Language Model. O "cérebro" que gera texto.
- **Agente** — LLM + memória + ferramentas + capacidade de decisão.
- **Tool calling** — quando o LLM "pede" para o sistema executar uma função (ex: ler arquivo).
- **StateGraph** — grafo onde cada nó é uma etapa do raciocínio do agente.
- **System prompt** — instrução fixa que define o comportamento do agente.
- **Temperature** — controla aleatoriedade do LLM. 0 = determinístico, 2 = caótico.
- **SSE (Server-Sent Events)** — protocolo HTTP para servidor "empurrar" dados ao cliente (usado para streaming).
- **Path traversal** — ataque que tenta acessar arquivos fora do diretório permitido usando `../`.
- **Arquitetura modular** — organização do código por feature (chat, config, agent) em vez de por camada técnica (routes, services, models).
- **Inversão de dependência** — princípio que diz "módulo de alto nível não depende de módulo de baixo nível; ambos dependem de abstrações".

---

## 12. Próximos passos (pós-bootcamp)

Quando o projeto base estiver pronto, evoluções naturais:

1. **RAG** — fazer o Megumin "lembrar" de documentação específica via embeddings
2. **MCP (Model Context Protocol)** — padrão para conectar agentes a ferramentas externas
3. **Avaliação** — usar Langfuse/LangSmith para medir qualidade das respostas
4. **Multi-agente** — equipe de Meguminis especializadas (frontend, backend, devops...)
5. **Deploy** — empacotar com Docker e disponibilizar publicamente

---

## 📌 Observações finais para o Claude Code

Ao trabalhar neste projeto, siga **rigorosamente**:

1. **Verifique a fase atual** (seção 6) antes de implementar — não avançar antes da hora, não implementar endpoints de fases futuras.
2. **Respeite a arquitetura modular** (seções 4 e 5) — código novo vai dentro do módulo apropriado, nunca em pastas planas.
3. **Aplique as 4 regras de ouro** (seção 5) — especialmente a Regra 1 (comunicação só via `__init__.py`).
4. **Respeite o escopo** (seção 7.2) — não adicionar features fora do plano (sem auth, sem banco, sem deploy).
5. **Calibre os comentários** (seção 8.3) — explique o "porquê", não o óbvio. Faça paralelos com Spring Boot quando ajudar.
6. **Siga as convenções de nomenclatura** (seção 8.1) — sem misturar `camelCase` em Python ou `snake_case` em variáveis TS.
7. **Personalidade vem por último** (Fase 7) — não polua código anterior com drama prematuro.
8. **Segurança é inegociável** (seção 7.1) — nunca pule validação de path nas ferramentas de arquivo.
9. **Quando em dúvida, pergunte** — é melhor pedir esclarecimento do que assumir e gerar código errado.
