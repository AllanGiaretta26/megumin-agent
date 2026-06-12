# 📋 Relatório Pós-Bootcamp v3 — Estabilização do Caminho Crítico e Polish UX

> **Período coberto:** 18/05/2026 (sessão única)
> **Foco:** Tool status confiável + contrato SSE tipado (Passo 1 — estabilização); polish de UX e a11y na Settings.
> **Continuação de:** [`relatorio-pos-bootcamp-v2.md`](relatorio-pos-bootcamp-v2.md) (v2)

---

## 📑 Índice

1. [Resumo executivo](#1-resumo-executivo)
2. [Linha do tempo](#2-linha-do-tempo)
3. [Branches criadas](#3-branches-criadas)
4. [Polish UX da Settings (atalhos de baixa prioridade)](#4-polish-ux-da-settings)
5. [Passo 1 — Estabilização do caminho crítico](#5-passo-1--estabilização-do-caminho-crítico)
6. [Investigação adicional — "modelo não chama tool"](#6-investigação-adicional)
7. [Aprendizados arquiteturais](#7-aprendizados-arquiteturais)
8. [Dívidas técnicas registradas hoje](#8-dívidas-técnicas-registradas-hoje)
9. [Dívidas anteriores fechadas](#9-dívidas-anteriores-fechadas)
10. [Onde paramos](#10-onde-paramos)
11. [Próximos passos](#11-próximos-passos)

---

## 1. Resumo executivo

Sessão de um único dia (18/05/2026) com dois eixos: **polish UX da Settings** (4 dívidas baixa prioridade do v2 + 3 follow-ups) e **Passo 1 da estabilização do caminho crítico** (atacando 3 dívidas técnicas do v2 — #1 temperature, #8 status de tool, #9 contrato SSE).

A vitória mais limpa foi a **substituição da heurística de status de tool por contrato explícito**: a heurística antiga (`output.startswith(("error","erro"))`) estava **100% errada** contra as mensagens reais das tools — todas começam com "Arquivo", "Diretório" ou "Acesso". Toda falha de tool vinha sendo reportada como `status=ok` para o frontend. Agora cada tool retorna um `ToolResult(status, content)` via mecanismo oficial `@tool(response_format="content_and_artifact")` do LangChain, e o grafo lê `tool_output.artifact.status` direto.

A surpresa mais útil foi descobrir que a **Dívida #1 (temperature) já estava resolvida no código** desde a `feat/provider-factory` (v1, etapa 10) — os relatórios estavam desatualizados. Princípio reforçado: o código manda, a documentação acompanha.

O Passo 1 fica pendente de PR (branch `refactor/critical-path-stabilization`, 2 commits, 9 testes pytest verdes). A dívida #26 — gpt-oss:120b ocasionalmente devolve `AIMessage.tool_calls` vazio — foi observada mas **não reproduzível em 5/5 retentativas** no mesmo dia; ficou registrada para revisitar.

---

## 2. Linha do tempo

### Bloco 1 — Polish UX da Settings (manhã/tarde)

- 4 dívidas baixa prioridade do v2 (#5 a11y forms, #6 lifespan, #7 label drama=0, #14 dropdown fallback).
- 2 follow-ups depois de validar via Chrome DevTools: textarea do chat-input ficou de fora da varredura inicial (#5 incompleta); password field exigia envolver tudo num `<form>` com `autoComplete` adequado.
- 1 polish cosmético: emoji 💾 do botão Salvar trocado pelo ícone lucide `Save`.

### Bloco 2 — Passo 1 — Estabilização

- **Sub-tarefa 1 (temperature)** — diagnóstico revelou estar já resolvida. Descartada sem mexer em código.
- **Sub-tarefa 2 (status de tool)** — heurística string-match substituída por `ToolResult` via `@tool` artifact. Tools migradas uma a uma (read_file → list_directory → write_file). 2 testes pytest.
- **Sub-tarefa 3 (contrato SSE)** — `astream` agora yielda `TextChunkEvent | ToolResultEvent` (discriminated union Pydantic v2), paridade byte-a-byte com legado. 7 testes pytest.
- **Investigação extra** — usuário observou modelo respondendo com JSON em texto ao invés de chamar tool. Investigação chegou a `bind_tools` + captura HTTP via openai logger; 5/5 retentativas funcionaram, sintoma transitório; patch DEBUG removido inteiro, dívida #26 registrada.

---

## 3. Branches criadas

| Branch | Status | Commits |
|---|---|---|
| `chore/low-priority-polish` | ✅ Merged via PR #7 | `91cb576` lifespan; `16b4c45` bubble label; `47cf9c2` settings UX (manual entry + a11y) |
| `main` (commits diretos pós-PR #7) | ✅ Aplicados | `d97ab39` chat textarea a11y; `60e4140` settings `<form>` wrap + autocomplete + ícone Save |
| `refactor/critical-path-stabilization` | ⏳ Pronta para PR | `3584c4b` pytest dep; `9574cb4` refactor tool status + SSE event contract |

> Decisão consciente de **commitar direto em `main` os 2 follow-ups do polish** (escopo pequeno, dependentes do PR #7 recém-merged).

---

## 4. Polish UX da Settings

### 4.1 Dívida #6 — `on_event("startup")` → lifespan

Substituído por `@asynccontextmanager async def lifespan(app)` em `backend/app/main.py`. Comportamento idêntico (continua capturando o config snapshot para `/config/restart-required`). Fecha o deprecation warning do FastAPI moderno.

### 4.2 Dívida #7 — Label "Megumin" em drama=0

`chat-message.tsx` recebe prop nova `assistantName?: string`. `chat-layout.tsx` decide via `(config?.personality.drama_level ?? 0) > 0 ? "Megumin" : "Assistant"` e propaga para `ChatContainer` → `ChatMessage`. **Sidebar e WelcomeScreen mantêm "Megumin"** como brand do app (não tracking de persona ativa).

### 4.3 Dívida #14 — Dropdown fallback para `/models`

Settings form ganhou estado `manualModelEntry`. Quando `/models` falha, retorna vazio, ou modelo salvo não está na lista, aparece link "Inserir manualmente" que troca o select por um `Input` livre. Link "Voltar ao dropdown" desfaz. Sem persistência além do componente.

### 4.4 Dívida #5 — Acessibilidade dos forms

- Todos inputs, selects e ranges ganharam `id` + `name` matching.
- Todos `<label>` ganharam `htmlFor` apontando para o campo.
- Language select (que não tinha `<label>`) ganhou `aria-label="Idioma"`.
- `PathPicker` exposto props `id`, `name`, `ariaLabel`.
- Chat textarea (`chat-input.tsx:59`) ganhou `id="chat-message"`, `name="chat-message"`, `aria-label="Mensagem"` — escapou da varredura inicial, fechado em commit follow-up.

### 4.5 Follow-up — `<form>` wrap + autocomplete + ícone Save

Chrome DevTools alertou:
- *"Password field is not contained in a form"* — settings-form era `<div>`, não `<form>`. Envolveu o conteúdo num `<form onSubmit={...}>` real, Cancel ganhou `type="button"`, Save ganhou `type="submit"` (removido `onClick`).
- *"Input elements should have autocomplete attributes"* — api-key recebeu `autoComplete="current-password"` (valor sugerido pelo Chrome, integra com password managers), base-url recebeu `autoComplete="url"`.
- Cosmético — emoji 💾 do botão Salvar trocado pelo ícone `<Save />` do lucide-react, alinhando com `Bot`, `FolderOpen`, `Globe`, `Info`, `Sparkles` usados nas seções.

---

## 5. Passo 1 — Estabilização do caminho crítico

Escopo original: 3 sub-tarefas atacando dívidas técnicas do v2 (#1 temperature, #9 contrato SSE, #8 status de tool). A ordem original foi alterada após diagnósticos.

### 5.1 Sub-tarefa 1 — Temperature (DESCARTADA)

Diagnóstico estático antes de mexer em código revelou que a dívida **já está resolvida**:

- `backend/app/modules/config/schemas.py:6` — `temperature: float = Field(default=0.7, ge=0.0, le=2.0)` em `PersonalitySettings`.
- `backend/app/modules/agent/providers/__init__.py:15` — `build_provider` lê `config.personality.temperature`.
- `backend/app/modules/agent/providers/ollama.py:18` — `ChatOllama(..., temperature=self._temperature)`.
- `backend/app/modules/agent/providers/openai_compat.py:26` — `ChatOpenAI(..., temperature=self._temperature)`.

A linha do `relatorio-fase-pos-bootcamp.md:188` ("`ChatOllama`/`ChatOpenAI` criados sem temperature") **não corresponde** ao código atual — provavelmente foi fechada no mesmo PR da `feat/provider-factory` (v1 etapa 10) mas a dívida não foi marcada como resolvida nos relatórios.

**Nada foi alterado no código.** Dívida #1 movida para a seção "fechadas" deste v3.

### 5.2 Sub-tarefa 2 — Tool status via `@tool` artifact

**Diagnóstico crítico:** heurística antiga em `graph.py:241` (`output.lower().startswith(("error","erro"))`) estava **100% errada** contra as mensagens reais — todas começam com "Arquivo", "Diretório" ou "Acesso", nenhuma com "error"/"erro". Todo erro de tool vinha sendo reportado como `status=ok`.

Trocou ordem: virou Sub-tarefa 2 (era 3), prioridade subiu porque é bug ativo.

**Mudanças aplicadas:**

| Arquivo | Mudança |
|---|---|
| `backend/app/modules/agent/tools/base.py` | **novo** — `@dataclass(frozen=True, slots=True) class ToolResult(status: Literal["ok","error"], content: str)`. Dataclass (não Pydantic) — container interno, nunca cruza HTTP. |
| `backend/app/modules/agent/tools/read_file.py` | Lógica extraída para `_read_file_impl(...) -> ToolResult`. `@tool(response_format="content_and_artifact")` retorna `(result.content, result)` |
| `backend/app/modules/agent/tools/list_directory.py` | Mesma estrutura |
| `backend/app/modules/agent/tools/write_file.py` | Mesma estrutura |
| `backend/app/modules/agent/graph.py` (~l.246) | Heurística removida. Lê `getattr(tool_output, "artifact", None)`. Se é `ToolResult` → usa `artifact.status`. Senão → fallback ruidoso: `status="error"` + `logger.error(...)` |

**Mecanismo:** `response_format="content_and_artifact"` do LangChain monta `ToolMessage(content=string_pro_LLM, artifact=ToolResult_pro_grafo)`. O LLM vê só a string; o grafo lê o objeto estruturado via `astream_events` no `on_tool_end`.

**Migração incremental verificada:** migrou só `read_file` primeiro. Smoke test com `read_file.invoke({"type":"tool_call",...})` confirmou que `ToolMessage.artifact` é instância de `ToolResult` com `status` correto. Depois migrou `list_directory` e `write_file`.

**Testes:** 2 em `backend/tests/agent/tools/test_read_file.py`:
- `test_read_file_returns_error_on_traversal` — `status == "error"` para `"../escape.txt"`
- `test_read_file_returns_ok_on_valid_path` — `status == "ok"` para arquivo válido

**Mini-bug pré-existente descoberto (não corrigido):** mensagem de path traversal aparece duplicada — `"Acesso negado: Acesso negado: '...'"`. `PathTraversalError.__str__` já carrega "Acesso negado:" e as tools prefixam de novo. Cosmético, fora do escopo.

### 5.3 Sub-tarefa 3 — Contrato SSE tipado

**Mudanças aplicadas:**

| Arquivo | Mudança |
|---|---|
| `backend/app/modules/agent/events.py` | **novo** — `TextChunkEvent(type="token", content)`, `ToolResultEvent(type="tool_call", tool, args, output, status)`, `AgentEvent = Annotated[Union[...], Field(discriminator="type")]`. Cada um expõe `to_sse_data() -> str` |
| `backend/app/modules/agent/graph.py` | Import `AsyncIterator`. `astream(...) -> AsyncIterator[AgentEvent]`. 3 yields convertidos: `yield token` → `TextChunkEvent(content=token)`; dict → `ToolResultEvent(...)`; fallback texto → `TextChunkEvent(content=...)` |
| `backend/app/modules/chat/router.py` | `isinstance(item, ToolResultEvent)` → `item.to_sse_data()`. `isinstance(item, TextChunkEvent)` → acumula `item.content` + `item.to_sse_data()`. `else` → `logger.error(...)` |

**Decisões deliberadas:**

- **Wire types ficam `"token"` e `"tool_call"`** (frontend não muda). `"tool_call"` é misnomer (carrega RESULTADO, não a chamada) — registrado como dívida #25 para rename coordenado em PR futuro.
- **`to_sse_data()` usa `json.dumps(self.model_dump())`**, NÃO `model_dump_json()`. Razão: defaults de escape Unicode divergem (Pydantic v2 default mantém UTF-8 literal; `json.dumps` default escapa para `\uXXXX`). Usar `json.dumps(dict)` preserva paridade byte-a-byte com o código legado.
- **`ValidationError` NÃO é capturado** no gerador. Princípio: falha ruidosa expõe bug latente em vez de mascarar. Mesmo espírito do fallback ruidoso da Sub-tarefa 2.
- **`done` e `error` permanecem construídos no router** (linhas 124/128) — são metadata do transporte SSE, não eventos do domínio do agente. Manter no router respeita a regra de direção de dependência do BRIEFING §5.
- **`events.py` mora em `modules/agent/`**, não em `shared/` — contrato é específico do domínio do agente.

**Testes:** 7 em `backend/tests/agent/test_events.py`:
- Paridade `TextChunkEvent` × legado: ASCII puro, Unicode (`EXPLOSÃO!!! 你好 — ação`), aspas duplas
- Paridade `ToolResultEvent` × legado: básico, args aninhado (`{"outer": {"inner": [1, 2, 3]}}`)
- `AgentEvent` resolve discriminated union corretamente via `TypeAdapter`
- `ToolResultEvent(status="OK")` levanta `ValidationError` (maiúsculo rejeitado por design)

---

## 6. Investigação adicional — "modelo não chama tool"

Durante teste manual da Sub-tarefa 3, o `gpt-oss:120b` algumas vezes respondeu com JSON em texto literal — `{"type":"function","function":"list_directory","arguments":{"path":"."}}` — em vez de gerar `tool_calls` estruturado no `AIMessage`. Investigação em 4 camadas (da mais barata para a mais cara):

### 6.1 `bind_tools` confirmado

- `backend/app/modules/agent/providers/base.py:18-24` — `get_llm_with_tools` chama `self.get_llm().bind_tools(tools)`.
- `backend/app/modules/agent/providers/openai_compat.py` — herda sem override.
- `backend/app/modules/agent/graph.py:72-73` — chama corretamente com as 3 tools reais.
- Log `tools=['read_file', 'list_directory', 'write_file']` confirma instâncias resolvidas (não strings).

**H1 descartada.**

### 6.2 Logging do request HTTP

Patch temporário em `backend/app/main.py` adicionou `StreamHandler(stdout)` ao logger `openai._base_client` (porque `getLogger("openai").setLevel(DEBUG)` sozinho não basta — uvicorn não propaga DEBUG do root para loggers de terceiros).

**Resultado:** captou URL, headers, request_id (`x-request-id`), status 200 OK. **Mas NÃO o body** — limitação da `openai-python`, que no nível DEBUG só loga metadata.

Request_ids do Ollama Cloud capturados (úteis para ticket de support futuro caso necessário).

### 6.3 Tentativa de reprodução com 5 execuções

Rodou `/chat/stream` 5x consecutivas com mesmo prompt ("liste os arquivos") em modo Agente, drama=0. **5/5 funcionaram** — tool chamada corretamente em todas, fluxo `call_llm → execute_tools → call_llm → format_response`.

Sem caso ruim na mão, não foi possível fazer diff "boa vs ruim". Por protocolo combinado: **para e reporta**.

### 6.4 Patch DEBUG removido

Usuário considerou converter o patch em "observabilidade leve permanente" — filter por string-match capturando só linhas com `request_id`. Avaliação honesta concluiu que era gambiarra:
- Filter casa string no conteúdo do log → depende de internals da `openai-python`, frágil em updates da lib.
- Use case ("correlação com support do Ollama Cloud") é hipotético — projeto nunca abriu ticket, não tem workflow.

**Patch DEBUG removido inteiro do `main.py`.** Volta ao estado pré-investigação. Se a dívida #26 reaparecer, re-aplicar leva 30 segundos.

### 6.5 Conclusão

Comportamento transitório e não-determinístico do `gpt-oss:120b`. Registrado como dívida #26.

---

## 7. Aprendizados arquiteturais

### 7.1 Código manda, doc acompanha

- **Onde surgiu:** Sub-tarefa 1 — diagnóstico revelou que dívida #1 (temperature) já estava resolvida no código desde `feat/provider-factory`, mas os relatórios v1 e v2 listavam como aberta.
- **Implicação:** sempre validar a premissa lendo o código antes de aplicar qualquer patch baseado em dívida documentada. Se houver conflito, **o código é a fonte da verdade** — a doc fica desatualizada, o código não mente.

### 7.2 Heurística no caminho crítico precisa validação empírica

- **Onde surgiu:** heurística `output.lower().startswith(("error","erro"))` parecia razoável em revisão estática, mas **0% das mensagens de erro das 3 tools** começam com essas strings (começam com "Arquivo", "Diretório", "Acesso").
- **Implicação:** não basta pensar sobre o que "deveria" começar com "error" — precisa confrontar com os dados reais. Heurística silenciosa em caminho crítico é pior do que ausência de checagem, porque dá falsa segurança.

### 7.3 `@tool(response_format="content_and_artifact")` é o padrão LangChain para separar visão-do-LLM da visão-do-grafo

- **Onde surgiu:** Sub-tarefa 2 precisava expor status estruturado para o grafo sem poluir o que o LLM lê na `ToolMessage.content`.
- **Implicação:** tools retornam tupla `(content_str, artifact_obj)`. LangChain monta `ToolMessage(content=string, artifact=objeto)`. O grafo acessa `tool_output.artifact` no `on_tool_end`. Evita gambiarra de sentinel prefix ("ERROR: ...") ou parsing de mensagem.

### 7.4 `model_dump_json()` ≠ `json.dumps(model_dump())` em escape de Unicode

- **Onde surgiu:** Sub-tarefa 3 precisava preservar serialização SSE byte-a-byte. Pydantic v2 default mantém UTF-8 literal; `json.dumps` default escapa para `\uXXXX`. São bytes diferentes apesar de JSON equivalente.
- **Implicação:** para paridade com código legado que usa `json.dumps(dict)`, usar `json.dumps(self.model_dump())` no `to_sse_data()`. Detalhe sutil, mas crítico quando o contrato HTTP não pode quebrar.

### 7.5 `openai-python` em DEBUG só loga metadata, não body

- **Onde surgiu:** investigação da dívida #26 tentou capturar request body para confirmar que `tools=[...]` chegava ao Ollama Cloud.
- **Implicação:** o SDK `openai-python` no nível DEBUG emite URL, headers, status, request_id — mas não o payload. Para body, precisaria monkey patch (Opção B) ou mitmproxy (Opção C). `httpx` em DEBUG tem a mesma limitação. Útil saber antes de gastar tempo investigando outras causas.

### 7.6 Gambiarra observatorial em produção custa mais do que rende

- **Onde surgiu:** discussão sobre converter o patch DEBUG em "filter permanente leve" capturando só `request_id`.
- **Implicação:** filter por string-match no conteúdo do log + dependência de internals de lib de terceiro + use case hipotético = código frágil que envelhece mal. **"Ou fica limpo, ou sai."** Se a necessidade voltar, re-aplicar o patch leva segundos; manter encantamento permanente cobra juros.

### 7.7 Não-determinismo de modelo dificulta diagnóstico

- **Onde surgiu:** dívida #26 — `gpt-oss:120b` ora chama a tool, ora não chama. 5/5 retentativas funcionaram, então não foi possível capturar caso "ruim" para fazer diff.
- **Implicação:** quando sintoma é transitório, vira **dívida registrada**, não correção. Se voltar a manifestar, capturar imediatamente (logs, prompt exato, request_id) antes do estado se perder.

---

## 8. Dívidas técnicas registradas hoje

Todas anotadas no docstring de topo de `backend/app/modules/agent/tools/base.py` (lugar visível, em git, junto com a definição do `ToolResult`):

| # | Item | Prioridade |
|---|---|---|
| **21** | Tools não capturam `OSError`/`PermissionError`/`UnicodeDecodeError` de I/O real. Exceções de baixo nível propagam para fora da tool e viram erro 500 no grafo. | Média |
| **24** | Modelo gera pseudo-tool-call como JSON em texto em vez de invocar a tool real (observado com gpt-oss:120b em modo Agente). Possíveis caminhos: prompt do modo mais firme, temperature mais baixa em modo agentic, troca de modelo. | Média |
| **25** | Wire `type="tool_call"` é misnomer (carrega RESULTADO da tool, não a chamada). Rename coordenado com frontend em PR futuro. | Baixa |
| **26** | `gpt-oss:120b` ocasionalmente devolve `AIMessage.tool_calls` vazio com JSON estruturado em `content`. Observado durante Sub-tarefa 3, não reproduzível em 5/5 retentativas no mesmo dia. Mitigação futura: retry com prompt reforçado, ou troca de modelo. | Média |

---

## 9. Dívidas anteriores fechadas

| # | Item | Como foi fechada |
|---|---|---|
| **#1** (v1/v2) | `temperature` da config não chega ao LLM | Já estava resolvida no código desde `feat/provider-factory` — descoberto no diagnóstico da Sub-tarefa 1, nenhuma mudança necessária. Relatórios estavam desatualizados. |
| **#5** (v1/v2) | Acessibilidade dos forms | id/name + htmlFor em todos os inputs/selects/ranges/textarea; aria-label onde não havia label; PathPicker com props; `<form>` wrap + autoComplete |
| **#6** (v1/v2) | `@app.on_event("startup")` deprecado | Migrado para lifespan context manager (`91cb576`) |
| **#7** (v1/v2) | Label "Megumin" mesmo em drama=0 | Prop `assistantName` no chat bubble (`16b4c45`) |
| **#8** (v1/v2) | Heurística frágil de status (`startswith "error"`) | Substituída por `ToolResult.status` via `@tool` artifact (`9574cb4`) |
| **#9** (v1/v2) | `astream` yielda `str \| dict` sem contrato | `TextChunkEvent` + `ToolResultEvent` discriminated union (`9574cb4`) |
| **#14** (v1/v2) | Modo avançado de input manual no dropdown | Toggle "Inserir manualmente" / "Voltar ao dropdown" (`47cf9c2`) |

---

## 10. Onde paramos

### Roadmap de prompts (estado mantido do v2)

| # | Prompt | Status |
|---|---|---|
| 1 | `personality.md` | ✅ Validado (com limitações conhecidas do tier system) |
| 2 | `agent.md` | ✅ Validado |
| 3 | `free_chat.md` | ✅ Validado |
| 4 | `autonomous_edit.md` | ❌ Bloqueado (sem decisão sobre confirmação interativa) |
| 5 | `planning.md` | ✅ Validado |
| 6 | `questions.md` | ✅ Validado |

### Estado do caminho crítico (novo no v3)

| Componente | Status |
|---|---|
| Tools — contrato de retorno | ✅ `ToolResult` estruturado, 3 tools migradas |
| Tools — testes | ⚠️ Só `read_file` tem testes (2). `list_directory` e `write_file` cobertos só por smoke test manual. |
| Grafo — leitura de status | ✅ Lê `artifact.status`, fallback ruidoso |
| Grafo — contrato de saída | ✅ `AsyncIterator[AgentEvent]` |
| SSE — serialização | ✅ Paridade byte-a-byte preservada |
| Frontend SSE | ✅ Não tocado, continua compatível |

### Branches abertas

- `refactor/critical-path-stabilization` — pronta para PR contra `main`. 2 commits (`3584c4b` pytest dep + `9574cb4` refactor). 9 testes pytest verdes.

### Configuração funcional atual

Mantida do v2:
- Provider: `openai_compatible`
- Modelo: `gpt-oss:120b` (Ollama Cloud)
- Base URL: `https://ollama.com/v1`
- Personalidade: `drama_level=0` (durante a sessão), `temperature=0.9`, `language=pt-BR`
- Project path de teste: `C:\dev\prj-agente-ai\megumin-agent-test`

---

## 11. Próximos passos

Sequência sugerida, em ordem de leverage decrescente:

1. **Abrir PR de `refactor/critical-path-stabilization` → main.** Sub-tarefas 2 e 3 do Passo 1 prontas. Testes verdes. Bloqueio: nenhum.

2. **Retestar com modelo grande externo** (Claude Sonnet via openai_compat, ou outro 70B+). Pendência herdada do v2 (#4 da lista de dívidas). Continua sendo o experimento de maior alavancagem — valida se as regressões de personalidade/tier do v2 são limitação de modelo pequeno ou design dos prompts. **Muda o roteiro do que vem depois.**

3. **Atacar dívida #2 do v2** — hidratação de tool calls no histórico. Depende de decisão UX (mostrar como card colapsável que persiste? recarregar a sessão recupera os blocos?). Não atacar sem essa decisão.

4. **Atacar dívidas #24 ou #26 se reaparecerem** — caminhos possíveis:
   - Retry com prompt reforçado quando `AIMessage.tool_calls` vier vazio mas `content` contiver JSON estruturado
   - Troca de modelo (modelo com melhor function calling sequencial)
   - Captura de payload via Opção B (monkey patch openai-python) para evidência

5. **`autonomous_edit.md`** — continua bloqueado por decisão arquitetural sobre confirmação interativa. Não destravar sem decidir primeiro.

6. **Dívida secundária**: testes para `list_directory` e `write_file` (paralelo aos 2 de `read_file`). Baixo custo, baixa prioridade — só fazer se for revisitar tools por outro motivo.

---

## 📌 Notas finais

- O caminho crítico (grafo → tools → SSE) agora tem **3 pontos de tipagem forte** que antes eram `str` solto: `ToolResult` (interno), `AgentEvent` (gerador→router), e o discriminator no payload SSE. Cada um falha ruidosamente se for violado, em vez de mascarar bug silencioso.
- A descoberta da dívida #1 já estar resolvida foi o **maior achado de baixo custo** da sessão: zero código mudou, mas o entendimento do estado real do sistema melhorou. Vale repetir a prática (validar premissa antes de aplicar patch) em cada sub-tarefa futura.
- A investigação da dívida #26 reforçou um padrão útil: quando o sintoma é não-determinístico e a infraestrutura de captura é cara, **registrar como dívida com critério de reativação** ("se voltar a manifestar X vezes, escalar para captura via Y") é mais sensato do que instalar observabilidade permanente especulativa.
- Branch `refactor/critical-path-stabilization` é a mais autocontida do projeto até hoje: zero mudança de contrato HTTP, zero mudança em frontend, ganho de tipagem em 3 camadas. PR de baixo risco.
