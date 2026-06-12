# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Start with `docs/relatorios/relatorio-pos-bootcamp-v4.md`** for the current project state, and [`ARCHITECTURE.md`](ARCHITECTURE.md) for the architecture overview. This file summarizes what you need to act; the reports under `docs/` explain why.

---

## Internal documentation

Lives in `docs/` (versioned). For the public, distilled architecture overview see [`ARCHITECTURE.md`](ARCHITECTURE.md) at the repo root. Suggested read order for the internal reports:

- `docs/relatorios/relatorio-pos-bootcamp-v4.md` — **current state**. Tool-path hardening (filesystem `OSError` → `ToolResult`), Megumin visual redesign + AI-generated avatar, forward-compat for the SSE tool-event rename (#25).
- `docs/relatorios/relatorio-pos-bootcamp-v3.md` — critical-path stabilization (typed tool status + typed SSE events), debts #21/#24/#25/#26.
- `docs/relatorios/relatorio-pos-bootcamp-v2.md` — prompt refactor, drama tier system, mode-aware Rule #5 in personality.
- `docs/relatorios/relatorio-pos-bootcamp-v1.md` — provider factory, dynamic models, post-bootcamp foundation work.
- `docs/arquitetura/BRIEFING-BOOTCAMP.md` — original architectural snapshot from the bootcamp (frozen at Phase 7). Still authoritative for module boundaries, naming conventions and security rules; execution details are out of date — cross-check with the reports above.
- `docs/manutencao/bugs-e-atencao.md` — running list of bugs and attention points.

---

## Commands

### Backend (inside `backend/`)

```powershell
# Install dependencies (including dev group)
uv sync --dev

# Run dev server
uv run uvicorn app.main:app --reload --port 8000

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/path/to/test_file.py -v
```

Python is pinned to **3.14** via `.python-version`. Use `uv` for all package management — never `pip` directly. Dev-only deps (currently just `pytest`) live under `[dependency-groups] dev` (PEP 735).

### Frontend (inside `frontend/`)

```bash
npm install
npm run dev          # http://localhost:3000 (Next.js 16, Turbopack)
npm run build
npm run lint
npx tsc --noEmit     # type check, used as smoke before commits
```

---

## Architecture

**Modular monolith** — organized by feature, not by technical layer.

```
backend/app/
├── main.py              # FastAPI bootstrap + router registration + lifespan
├── core/                # app-specific infrastructure (settings, exceptions, path sandbox)
├── modules/
│   ├── chat/            # conversation history, session management, SSE router
│   ├── config/          # load/save config.json, model selection, runtime snapshot
│   └── agent/           # LangGraph StateGraph, 5 modes, tools, LLM providers
│       ├── events.py    # typed AgentEvent union (TextChunkEvent | ToolResultEvent)
│       ├── tools/base.py  # ToolResult dataclass (status + content)
│       └── ...
└── shared/              # neutral utilities (logger, templating, global types)
```

**Frontend** (`frontend/`) mirrors the backend module split: `features/chat/`, `features/config/`, `features/modes/`.

### Critical contracts on the agent path

Two recently-introduced contracts on the stream pipeline — if you touch the graph, the tools, or the SSE serializer, you'll cross them:

- **`ToolResult`** (`modules/agent/tools/base.py`) — frozen dataclass `(status: Literal["ok","error"], content: str)`. Tools return it via `@tool(response_format="content_and_artifact")`; the graph reads `tool_output.artifact.status`. Noisy fallback (`status="error"` + log) if the artifact isn't a `ToolResult`.
- **`AgentEvent`** (`modules/agent/events.py`) — Pydantic v2 discriminated union of `TextChunkEvent` and `ToolResultEvent`. The `astream` generator yields events, the chat router dispatches by `isinstance` and serializes via `to_sse_data()` (uses `json.dumps(self.model_dump())` — **not** `model_dump_json()` — to preserve byte parity with the legacy SSE format). `ValidationError` is intentionally not caught.

### Dependency rules (enforced)

- All inter-module imports go through the module's `__init__.py` — never import internal files directly.
- Flow is one-directional: `router → service → core/shared`. `chat` may use `agent`; `agent` must not use `chat`.
- `core/` is app-specific infrastructure; `shared/` is project-agnostic utilities.

### Agent modes

The agent has exactly **5 modes** (one active at a time):

| Mode ID | UI label | Writes files? | Needs `project_path`? |
|---|---|:---:|:---:|
| `agent` | Agente | ✅ | ✅ |
| `planning` | Planejamento | ❌ | ✅ |
| `autonomous_edit` | Edição Autônoma | ✅ | ✅ |
| `questions` | Dúvidas | ❌ | ✅ |
| `free_chat` | Conversa Livre | ❌ | ❌ |

Each mode lives in `modules/agent/modes/` and has a matching system prompt in `modules/agent/prompts/`. `autonomous_edit` is currently blocked pending the architectural decision on interactive confirmation (see v1/v2 reports).

---

## Critical rules

1. **Project phase:** all 7 bootcamp phases are complete. Current work is post-bootcamp stabilization — see `docs/relatorios/relatorio-pos-bootcamp-v4.md`. The phase-gating logic of the bootcamp era no longer applies; ship work behind PRs, not phase numbers.
2. **Path sandbox:** every file tool must validate that the resolved path stays inside `project_path`. Path traversal (`../`, absolute paths) must be rejected.
3. **`config.json` is gitignored** — never commit it. API keys must be masked (`***`) in GET responses and round-trip via the sentinel pattern (`PUT /config` and `POST /models` accept `"***"` meaning "keep the saved key").
4. **CORS** is restricted to `http://localhost:3000`.
5. **No scope creep:** no auth, no database, no multi-agent, no RAG, no deploy. See `docs/arquitetura/BRIEFING-BOOTCAMP.md §7.2`.

---

## Naming conventions

| Context | Convention |
|---------|-----------|
| Python files | `snake_case.py` |
| Python classes | `PascalCase` |
| Python functions/vars | `snake_case` |
| Python constants | `UPPER_SNAKE_CASE` |
| TypeScript files | `kebab-case.tsx` |
| React components | `PascalCase` |
| TS functions/vars | `camelCase` |
| React hooks | `useXxx` |
| HTTP endpoints | `kebab-case` in URL |
| JSON fields | `snake_case` (both sides — no conversion layer) |

Backend: type hints required on all public functions. Frontend: `strict: true` TypeScript, no `any` without a justifying comment.

---

## Comments policy

- **Do comment:** non-obvious "why" decisions; first appearance of AI-ecosystem concepts (TypedDict, StateGraph); Spring Boot analogies when they clarify.
- **Don't comment:** what obvious code already says; basic Python/TS syntax.

---

## LLM / personality

Two providers, picked at runtime via `config.json`:

- **`ollama`** — local Ollama on `:11434` (default for offline development)
- **`openai_compatible`** — any OpenAI-compatible endpoint (currently `gpt-oss:120b` on Ollama Cloud at `https://ollama.com/v1`)

The factory in `modules/agent/providers/__init__.py` reads `provider`, `model_name`, `api_base_url`, `api_key`, and `personality.temperature` from `AppConfig` and builds the right provider. `ChatService` is fresh per request, so saved config changes apply on the next chat without a restart.

### Personality

Injected as a system prompt via `personality.md`, with a tier system on canonical bordões (`(N+)` — e.g. `"EXPLOSÃO!!!" (76+)`). `drama_level=0` triggers a **full bypass** of personality at `graph.py:_select_mode` — the agent runs with the mode prompt only, no Megumin voice at all. Tier annotations are textual prescription, not deterministic enforcement; leakage between tiers has been observed on `gpt-oss:120b` (see v3, debt #26).

Small local models (qwen3.5:9b, llama3.1:8b, gemma4:e4b) execute tools correctly but tend to ignore roleplay instructions. For full personality fidelity, use 13B+ models or external APIs (OpenRouter, Gemini).

---

## Documentation — update without being asked

Every task that adds, changes or removes behavior **must** update the relevant docs before closing. Do not wait for the user to request it.

`docs/` is **versioned** (committed). `CLAUDE.md` and `AGENTS.md` stay gitignored (local AI guidance).

| What changed | What to update |
|---|---|
| Module boundary, contract, mode, dependency rule, or LLM/provider wiring | `ARCHITECTURE.md` (repo root) — the public architecture overview, kept in sync with reality |
| End of a work session (features shipped, debts opened/closed) | New or updated report under `docs/relatorios/` |
| Bug found or attention point worth tracking | `docs/manutencao/bugs-e-atencao.md` |
| Architectural decision with a trade-off | **Recommended:** an ADR at `docs/adr/ADR-NNN-<slug>.md` (create the `docs/adr/` folder on first need). Use `Status: Accepted`; mark a superseded ADR `Status: Superseded by ADR-NNN`. Not yet adopted — no ADRs exist today. |

