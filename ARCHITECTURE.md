# Arquitetura

Visão geral da arquitetura do **Megumin Agent**. Para instalação e uso, veja o [`README.md`](README.md);
para o histórico de decisões e o "porquê" de cada escolha, veja os relatórios em [`docs/`](docs/).

---

## Visão geral

O projeto é um **monolito modular**: organizado por *feature*, não por camada técnica. Cada módulo
é autocontido e expõe sua API pública pelo próprio `__init__.py`. Não há banco de dados, autenticação
ou múltiplos serviços — é um backend FastAPI + um frontend Next.js, ambos rodando localmente.

```
megumin-agent/
├── backend/    # FastAPI + LangGraph (Python, uv)
└── frontend/   # Next.js 16 + React 19 (TypeScript, npm)
```

---

## Estrutura de pastas

### Backend (`backend/app/`)

```
backend/app/
├── main.py              # bootstrap FastAPI + registro de routers + lifespan
├── core/                # infraestrutura específica do app (settings, exceptions, sandbox de path)
├── modules/
│   ├── chat/            # histórico de conversa, sessões, router SSE
│   ├── config/          # load/save de config.json, seleção de modelo, snapshot de runtime
│   └── agent/           # StateGraph (LangGraph), 5 modos, tools, providers de LLM
│       ├── events.py    # união tipada AgentEvent (TextChunkEvent | ToolResultEvent)
│       ├── tools/base.py  # dataclass ToolResult (status + content)
│       ├── modes/       # um arquivo por modo
│       ├── prompts/     # system prompt correspondente a cada modo
│       └── providers/   # factory de provider de LLM
└── shared/              # utilitários neutros (logger, templating, tipos globais)
```

### Frontend (`frontend/src/`)

O frontend espelha o recorte do backend por feature:

```
frontend/src/
├── app/                 # rotas Next.js
├── components/          # layout e UI base (shadcn/ui)
└── features/
    ├── chat/            # chat + streaming
    ├── config/          # tela de Settings
    └── modes/           # seleção de modo
```

---

## Contratos críticos do caminho do agente

Dois contratos tipados governam o pipeline de streaming. Quem mexer no grafo, nas tools ou no
serializador SSE vai cruzar com eles.

### `ToolResult` — `modules/agent/tools/base.py`

Dataclass *frozen* `(status: Literal["ok", "error"], content: str)`. As tools a retornam via
`@tool(response_format="content_and_artifact")`; o grafo lê `tool_output.artifact.status`. Se o
artefato não for um `ToolResult`, há um *fallback* ruidoso (`status="error"` + log). Falhas reais de
filesystem (`OSError`/`PermissionError`) são capturadas e viram `ToolResult(status="error", ...)`,
sem escapar como erro 500 no grafo.

### `AgentEvent` — `modules/agent/events.py`

União discriminada (Pydantic v2) de `TextChunkEvent` e `ToolResultEvent`. O gerador `astream` produz
esses eventos; o router de chat despacha por `isinstance` e serializa via `to_sse_data()`. A
serialização usa `json.dumps(self.model_dump())` — **não** `model_dump_json()` — para preservar
paridade de bytes com o formato SSE legado. `ValidationError` **não** é capturado de propósito.

---

## Regras de dependência (obrigatórias)

- Todo import entre módulos passa pelo `__init__.py` do módulo — nunca importe arquivos internos
  diretamente.
- O fluxo é unidirecional: `router → service → core/shared`. `chat` pode usar `agent`;
  `agent` **não** pode usar `chat`.
- `core/` é infraestrutura específica do app; `shared/` é utilitário agnóstico de projeto.

---

## Os 5 modos do agente

Exatamente **5 modos**, um ativo por vez. Cada modo vive em `modules/agent/modes/` e tem um system
prompt correspondente em `modules/agent/prompts/`.

| Modo | UI | Escreve arquivos? | Precisa de `project_path`? |
|---|---|:---:|:---:|
| `agent` | Agente | ✅ | ✅ |
| `planning` | Planejamento | ❌ | ✅ |
| `autonomous_edit` | Edição Autônoma | ✅ | ✅ |
| `questions` | Dúvidas | ❌ | ✅ |
| `free_chat` | Conversa Livre | ❌ | ❌ |

---

## Fluxo de uma mensagem

```
POST /chat/stream
   → ChatService (instância nova por request)
      → StateGraph do LangGraph (seleção de modo + personalidade)
         → LLM (provider via factory) + tool calling
            → eventos AgentEvent (astream)
               → to_sse_data() → resposta SSE (streaming em tempo real no frontend)
```

`ChatService` é recriado a cada request, então mudanças salvas em `config.json` valem na próxima
conversa sem reiniciar o servidor.

---

## Sandbox de arquivos

Toda tool de arquivo valida que o caminho resolvido permanece **dentro** do `project_path`.
Path traversal (`../`, caminhos absolutos) é rejeitado. As tools disponíveis são `read_file`,
`list_directory` e `write_file`.

---

## Providers / LLM

Dois providers, escolhidos em runtime via `config.json`:

- **`ollama`** — Ollama local em `:11434` (padrão para desenvolvimento offline).
- **`openai_compatible`** — qualquer endpoint compatível com a API OpenAI.

A factory em `modules/agent/providers/__init__.py` lê `provider`, `model_name`, `api_base_url`,
`api_key` e `personality.temperature` de `AppConfig` e constrói o provider certo.

A personalidade é injetada como system prompt (`personality.md`), com um sistema de *tiers* sobre os
bordões canônicos. `drama_level=0` faz *bypass* total da personalidade — o agente roda só com o
prompt do modo.

---

## Documentação interna

O "porquê" de cada decisão está nos relatórios versionados:

- [`docs/relatorios/`](docs/relatorios/) — relatórios de sessão pós-bootcamp (v1–v4), o estado atual.
- [`docs/arquitetura/BRIEFING-BOOTCAMP.md`](docs/arquitetura/BRIEFING-BOOTCAMP.md) — snapshot
  arquitetural original (congelado na Fase 7), autoritativo para fronteiras de módulo e convenções.
- [`docs/manutencao/bugs-e-atencao.md`](docs/manutencao/bugs-e-atencao.md) — bugs e pontos de atenção.
