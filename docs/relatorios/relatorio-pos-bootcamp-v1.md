# 📋 Relatório da Fase Pós-Bootcamp — Agent AI Megumin

> **Período coberto:** 15/05/2026 (fim do bootcamp) → 16/05/2026 (sessão atual)
> **Foco:** Engenharia de prompts, correção de bugs, refinamento de UX, fidelidade à personagem.

---

## 📑 Índice

1. [Resumo executivo](#1-resumo-executivo)
2. [Linha do tempo da sessão](#2-linha-do-tempo-da-sessão)
3. [Branches criadas](#3-branches-criadas)
4. [Bugs corrigidos e pontos de atenção (atualizado)](#4-bugs-corrigidos-e-pontos-de-atenção-atualizado)
5. [Decisões arquiteturais tomadas](#5-decisões-arquiteturais-tomadas)
6. [Dívidas técnicas registradas](#6-dívidas-técnicas-registradas)
7. [Onde paramos](#7-onde-paramos)
8. [Próximos passos](#8-próximos-passos)

---

## 1. Resumo executivo

A fase pós-bootcamp atacou três frentes principais:

- **Engenharia de prompts** — auditoria estruturada dos 5 prompts de modo + sistema de personalidade, com reescrita de 4 deles (`personality`, `agent`, `study→free_chat`, `planning`).
- **Arquitetura de injeção** — refatoração do sistema de templating com `SafeDict`, inversão da ordem de injeção (personalidade primeiro), fast-path para drama=0.
- **Conectividade real com modelos** — descoberta e correção de um bug arquitetural sério: o backend ignorava completamente a config do `config.json` para escolher provider/modelo. Implementação de provider factory + dropdown dinâmico + banner de aviso.

**Resultado:** projeto evoluiu de "MVP funcional com personalidade rasa" para "produto polido com Megumin viva, suporte real a múltiplos providers, e UX de configurações fluida".

---

## 2. Linha do tempo da sessão

### Etapa 1 — Diagnóstico inicial
- Discussão sobre dor real (prompts rasos) + qual modelo em uso (8B-9B local + chave Ollama Cloud)
- Decisão: atacar engenharia de prompts primeiro (maior alavancagem para todos os modos)

### Etapa 2 — Auditoria dos prompts
- Claude Code executou auditoria estruturada dos 5 prompts + sistema de personalidade
- Ranking de prioridade gerado: `personality > agent > study > autonomous_edit > planning > questions`
- 7 perguntas arquiteturais respondidas

### Etapa 3 — Reescrita do `personality.md`
- Calibração contínua de drama (5 faixas: 0 / 1-25 / 26-50 / 51-75 / 76-100)
- Faixa 0 = personalidade desligada
- Vocabulário canônico Megumin expandido (entrada/execução/conclusão/tsundere)
- 5 few-shots calibrados
- 5 regras inquebráveis

### Etapa 4 — Templating e injeção
- Novo módulo `app/shared/templating.py` (`SafeDict` + `render_template`)
- Inversão da ordem: personality vem antes do prompt de modo
- `language` da config finalmente chega ao prompt
- Fast-path para drama=0 (early return sem concatenar personality)

### Etapa 5 — Reescrita do `agent.md`
- Documento operacional puro (sem persona misturada)
- "Regra dos 3 passos" para escrever arquivo (ler → anunciar → executar)
- Formato de resposta padronizado (anúncio / tools / resumo final)
- Tratamento de erro de tool + anti-loop explícito

### Etapa 6 — Tool call display (não estava no ranking, surgiu de bug)
- Descoberta: tool results sumiam no chat. Causa: backend descartava `on_tool_end` + modelo pequeno não sintetizava resultado no texto final
- Solução: novo evento SSE `tool_call` + componente `ToolCallBlock` colapsável no frontend
- Ajuste posterior: blocos movidos para baixo do texto (ordem natural de leitura)

### Etapa 7 — Renomeação `study` → `free_chat`
- Auditoria havia apontado colisão "professor objetivo" vs "Megumin arquimaga"
- Discussão sobre escopo: usuário pediu liberar como "chat geral" inspirado em chat de IA
- Renomeação completa (backend + frontend) com 6 tarefas estruturadas
- Novo prompt com regras de incerteza, redirecionamento de tópicos sensíveis, exemplos por domínio

### Etapa 8 — Reescrita do `planning.md` (v1 + v2)
- v1: passos com sub-bullets — modelo pequeno ignorou estrutura aninhada
- v2: passos viraram blocos H3 com `**Por quê:**` e `**Como validar:**` em linhas próprias + checklist obrigatório no topo
- Teste com modelo pequeno v2: ainda falhou (limite cognitivo do 8B-9B)

### Etapa 9 — Descoberta crítica: providers ignoram config
- Tentativa de testar prompt v2 com modelo grande (Ollama Cloud) via OpenAI-compat
- Dashboard não registrava uso. Investigação revelou: `AgentService` instancia `OllamaProvider` hardcoded, providers leem de `app.core.config.settings` (Pydantic .env), nunca do `AppConfig`
- Resultado: TODOS os testes anteriores rodaram no `llama3.1:8b` local, independente do que a UI mostrava

### Etapa 10 — Provider factory
- Branch `feat/provider-factory`
- `build_provider(config)` em `providers/__init__.py`
- `OllamaProvider` e `OpenAICompatProvider` refatorados para receber config explícita
- `AgentService` recebe config injetada
- **Primeira vitória real**: Ollama Cloud registrou 0.2% session / 0.1% weekly usage

### Etapa 11 — Dropdown dinâmico
- Branch `feat/dynamic-model-list`
- Endpoint `/models` generalizado para chamar API do provider ativo (Ollama local ou OpenAI-compat)
- Frontend busca modelos com debounce de 500ms quando provider/url/key mudam
- 39 modelos do Ollama Cloud listados corretamente

### Etapa 12 — Banner restart-required
- Branch `feat/restart-required-banner`
- Snapshot da config crítica no boot do backend
- Endpoint `/config/restart-required` compara snapshot vs disco
- Descoberta posterior: `ChatService` é instanciado fresh por request — mudanças JÁ aplicam sem restart. Texto do banner ajustado para "Mudanças aplicadas a partir das próximas conversas"

### Etapa 13 — Fix do `/models` (sentinel + reset de base_url)
- Branch `fix/models-from-form-data`
- Bug capturado: trocar provider sem salvar disparava request com mistura de campos novos + base_url antigo → 404 → 502
- POST `/models` aceitando params no body (sem ler do disco)
- Sentinel `"***"` para api_key salva (backend resolve antes de chamar list_models)
- Reset automático de `api_base_url` ao trocar provider (defaults por provider)

### Etapa 14 — Validação final
- Todos os 7 passos do teste manual passaram
- Issues de acessibilidade nos forms identificados (sem `id`/`name`, sem `<label htmlFor>`)
- 502 intermitente sumiu após o fix do reset de base_url

---

## 3. Branches criadas

| Branch | Status | Conteúdo |
|---|---|---|
| `refactor/personality-refactor` | ✅ Merged | personality.md + agent.md + templating + fast-path drama=0 |
| `feat/tool-call-display` | ✅ Merged | Evento SSE tool_call + ToolCallBlock colapsável |
| `refactor/free-chat-mode` | ✅ Merged | Renomeação study → free_chat + prompt expandido |
| `refactor/planning-prompt` | ✅ Merged | planning.md v2 |
| `feat/provider-factory` | ✅ Merged | Provider factory + config injetada |
| `feat/dynamic-model-list` | ✅ Merged | Dropdown dinâmico de modelos |
| `feat/restart-required-banner` | ✅ Merged | Banner azul informativo |
| `fix/models-from-form-data` | ✅ Pronto pra merge | POST /models + sentinel + reset base_url |

---

## 4. Bugs corrigidos e pontos de atenção (atualizado)

> Esta seção substitui o `bugs-e-atencao.md` original, agregando o histórico anterior + tudo descoberto/corrigido nesta fase.

### 4.1 Bugs corrigidos (histórico completo)

#### Fase 5 (bootcamp)
- **Tabelas markdown renderizando como texto plano** — corrigido com `remark-gfm`.

#### Fase 6 (bootcamp)
- **Campo Api Key usando `***` como texto editável** — corrigido separando `newApiKey` do valor do backend.
- **Botão "Mostrar" revelando `***`** — corrigido limitando toggle a chaves digitadas na sessão atual.
- **Emojis nas seções de configurações** — substituídos por ícones lucide-react.

#### Fase 7 (bootcamp)
- **`LoadingBubble` duplicado durante streaming** — corrigido com flag `isStreaming`.
- **Cursor de streaming preso indefinidamente** — corrigido com limpeza após o loop.
- **Resposta não aparecia após execução de tools** — corrigido via fallback `on_chain_end + format_response`.

#### Fase pós-bootcamp (esta sessão)
- **Personalidade Megumin rasa** — `personality.md` reescrito com calibração contínua, vocabulário canônico, few-shots, regras inquebráveis. Funcionou plenamente com modelos pequenos (não só grandes).
- **Colisão de identidade no modo Estudo** — "professor objetivo" vs "Megumin arquimaga" reconciliado como "Megumin atuando como mestra". Posteriormente renomeado para Conversa Livre com escopo geral.
- **Tool calls invisíveis no chat** — após execução, resultado da tool sumia. Corrigido com novo evento SSE + componente ToolCallBlock colapsável (Cursor-style).
- **`agent.md` genérico** — reescrito como documento operacional puro com "Regra dos 3 passos", formato de resposta padronizado, tratamento de erro, anti-loop.
- **🔴 Provider/modelo da config ignorados pelo backend** — bug arquitetural sério: AgentService instanciava OllamaProvider hardcoded apontando para localhost, ignorando `config.json`. Corrigido com provider factory.
- **Dropdown de modelos estático** — corrigido com endpoint `/models` dinâmico que consulta o provider ativo (Ollama local OU OpenAI-compat).
- **Trocar provider não resetava `api_base_url`** — corrigido com defaults por provider no frontend.
- **POST /models não funcionava com chave salva** — corrigido com sentinel `"***"` (backend resolve antes de chamar list_models).
- **502 intermitente ao trocar provider** — resolvido indiretamente pelo reset automático de base_url (eliminou a janela de race condition).
- **Banner "reinicie backend" textualmente incorreto** — ajustado para "Mudanças aplicadas a partir das próximas conversas" após descoberta de que ChatService é fresh por request.

### 4.2 Pontos de atenção atuais

#### Personalidade Megumin
✅ **Resolvido para modelos grandes.** Confirmado funcionando com `gpt-oss:120b` via Ollama Cloud.
⚠️ **Modelos < 13B** continuam tendo aderência parcial a instruções complexas, mas o novo `personality.md` melhorou significativamente até em 8B-9B.

#### Streaming com tools (limitação conhecida)
Fallback `on_chain_end + format_response` continua necessário. Tool calls agora têm captura própria via novo evento SSE, então o resultado não some mais.

#### Anúncio antes de escrever (Modo Agente)
✅ **Resolvido** com a Regra dos 3 Passos no `agent.md`. Modelos pequenos agora seguem o padrão de anunciar antes de chamar `write_file` na maioria dos casos.

#### Confirmação interativa no Modo Agente
❌ **Não implementada.** Por design, o projeto é REST stateless — "anunciar" significa apenas texto antes da tool call, sem pausa real. O usuário levantou que isso torna a fronteira `agent ↔ autonomous_edit` indistinguível na prática. Decisão: pular para focar nos prompts. **Pendência crítica que bloqueia a reescrita do `autonomous_edit.md`.**

#### Persistência do histórico
❌ **Continua in-memory.** Reiniciar backend apaga todo o histórico. Aceitável para escopo atual.

#### Hidratação de tool calls no histórico
❌ **Tool calls não são persistidos.** Ao recarregar uma sessão, mensagens passadas perdem os blocos visuais de tool. Backend só guarda texto.

#### Testes automatizados
⚠️ Apenas sandbox de segurança tem cobertura. `templating.py` e o provider factory são candidatos óbvios para a primeira suíte.

#### Outras dívidas técnicas conhecidas
- `temperature` da config não chega ao LLM (`ChatOllama`/`ChatOpenAI` criados sem temperature)
- `@app.on_event("startup")` é deprecado em FastAPI moderno (usar lifespan async context manager)
- `astream` agora yielda `str | dict` — contrato implícito sem modelo Pydantic
- Heurística de status de tool (`startswith "error"`) é frágil — idealmente tools sinalizariam status explicitamente
- Frontend label do balão exibe "Megumin" mesmo com `drama=0` (deveria virar "Assistant")
- `personality.md:122` ainda menciona "Modo Estudo / Modo Dúvidas" — corrigir junto da reescrita do `questions.md`
- Issues de acessibilidade nos forms (`<input>` sem `id`/`name`, `<label>` sem `htmlFor`)
- Removido input livre de fallback no dropdown — sem ele, se `/models` falhar, usuário não consegue digitar manualmente (proposta: link "modo avançado")

---

## 5. Decisões arquiteturais tomadas

### Templating de prompts
**Decisão:** `str.format_map(SafeDict(...))` em vez de `str.replace`.
**Justificativa:** placeholders ausentes não quebram o boot. Prompts podem evoluir adicionando/removendo variáveis sem coordenação rígida.
**Local:** `app/shared/templating.py` (Regra 4 das regras de ouro — utilitário neutro).

### Ordem de injeção do system prompt
**Decisão:** `personality + "\n\n" + mode.system_prompt` (personality primeiro).
**Justificativa:** modelos pequenos (8B-9B) ancoram identidade no primeiro parágrafo do system prompt.

### Fast-path drama=0
**Decisão:** early return retorna só o prompt do modo, sem concatenar personality.
**Justificativa:** modelo pequeno tendia a ignorar a "faixa 0" e responder como Megumin. Pular a injeção elimina o problema.

### Renomeação `study` → `free_chat`
**Decisão:** renomear arquivos, classes, enums (não só label visível).
**Justificativa:** evitar dívida cognitiva entre código (`study`) e UI (`Conversa Livre`).
**Trade-off aceito:** clientes HTTP antigos com `"mode": "study"` recebem 400. Aceitável (projeto single-user).

### Provider factory
**Decisão:** factory consome `AppConfig` em runtime, injetado em `AgentService`.
**Justificativa:** desfez o acoplamento entre config Pydantic do `.env` e config persistida do usuário. Agora o que está no `config.json` realmente afeta o comportamento.

### Sentinel `"***"` para api_key
**Decisão:** GET `/config` retorna `"***"` em vez da chave real. POST `/models` aceita `"***"` e resolve para a chave salva no backend.
**Justificativa:** chave nunca trafega de volta para o frontend após salva. Frontend precisa poder testar config sem ter a chave em mãos.

### Banner informativo (não bloqueante)
**Decisão:** banner azul "Mudanças aplicadas a partir das próximas conversas" em vez de banner amarelo "Reinicie o backend".
**Justificativa:** descoberta de que `ChatService` é fresh por request — mudanças aplicam automaticamente. Banner serve para streams em andamento e UX defensiva.

### Tool call display: blocos colapsáveis abaixo do texto
**Decisão:** padrão Cursor/Claude Code — texto da IA primeiro, tool calls colapsadas embaixo.
**Justificativa:** ordem natural de leitura (resumo executivo antes do detalhe técnico). Chat fica limpo, expansível sob demanda.

---

## 6. Dívidas técnicas registradas

Lista priorizada para próximas frentes:

| # | Item | Esforço | Prioridade |
|---|---|---|---|
| 1 | `temperature` da config não chega ao LLM | Baixo | Média |
| 2 | Hidratação de tool calls no histórico (recarregar sessão perde blocos) | Médio | Média |
| 3 | `personality.md:122` ainda menciona "Modo Estudo" | Baixo | Baixa (fazer junto do `questions.md`) |
| 4 | Re-testar prompts com modelo grande (`personality`, `agent`, `free_chat`) | Baixo | Alta (validação) |
| 5 | Acessibilidade dos forms (`id`/`name`/`label htmlFor`) | Médio | Baixa |
| 6 | `@app.on_event("startup")` deprecado | Baixo | Baixa |
| 7 | Frontend label do balão exibe "Megumin" mesmo com drama=0 | Baixo | Baixa |
| 8 | Heurística frágil de status de tool (`startswith "error"`) | Médio | Baixa |
| 9 | `astream` yielda `str \| dict` sem modelo Pydantic | Médio | Baixa |
| 10 | Confirmação interativa no Modo Agente (destrava `autonomous_edit.md`) | Alto | Média |
| 11 | Persistência de sessões (in-memory → SQLite/JSON) | Médio | Baixa |
| 12 | Testes automatizados (`templating.py`, factory, smoke da API) | Médio | Média |
| 13 | Extrair `build_system_prompt()` como função pura para testabilidade | Baixo | Baixa |
| 14 | Modo avançado de input manual no dropdown quando `/models` falha | Baixo | Baixa |
| 15 | 502 intermitente se voltar — blindar com debounce maior + skip de combinação inválida | Baixo | Baixa (monitorar) |

---

## 7. Onde paramos

### Estado atual do roadmap de prompts

| # | Prompt | Status |
|---|---|---|
| 1 | `personality.md` | ✅ Reescrito e validado |
| 2 | `agent.md` | ✅ Reescrito e validado |
| 3 | `study.md` → `free_chat.md` | ✅ Renomeado e expandido |
| 4 | `autonomous_edit.md` | ❌ **Bloqueado** pela decisão sobre confirmação interativa |
| 5 | `planning.md` | ✅ Reescrito (v2) |
| 6 | `questions.md` | ❌ **Pendente** |

### Último contexto da conversa

Acabamos de discutir que ainda faltam **2 prompts**, não 1 como eu havia afirmado por engano:
- `autonomous_edit.md` (bloqueado)
- `questions.md` (próximo viável)

A proposta na mesa era esboçar o `questions.md` (rápido, auditoria deu 4/5, faltava apenas formato de citação + snippets), mas o usuário não confirmou ainda — pediu este relatório antes.

### Branches abertas

- `fix/models-from-form-data` — pronta para merge (testes passaram, sem pendências).

### Configuração funcional atual

- Provider: `openai_compatible`
- Modelo: `gpt-oss:120b` (Ollama Cloud)
- Base URL: `https://ollama.com/v1`
- API key: configurada e funcional
- Personalidade: drama_level=70, temperature=0.9, language=pt-BR
- Project path: `C:\dev\prj-agente-ai\megumin-agent-test`

---

## 8. Próximos passos

### Opções imediatas

**A) Reescrever `questions.md`** (rápido, fecha o ranking de prompts viáveis)
- Auditoria deu 4/5 — só falta formato padronizado de citação de arquivo (`path:linha`) e snippets de código no resultado
- Esforço: baixo
- Pode ser feito junto da correção do `personality.md:122`

**B) Atacar dívidas técnicas críticas**
- `temperature` da config não chega ao LLM (item #1 da lista)
- Hidratação de tool calls no histórico (item #2)
- Re-testar prompts antigos com modelo grande para confirmar que tudo continua funcionando (item #4)

**C) Destravar `autonomous_edit.md` via confirmação interativa**
- Implementar pausa real entre anúncio e execução no Modo Agente
- Esforço alto (backend + frontend, mexe em ciclo de vida do StateGraph)
- Destrava a reescrita do prompt bloqueado

**D) Polimento UX**
- Acessibilidade dos forms (a11y)
- Label do balão quando drama=0
- Modo avançado no dropdown

**E) Testes automatizados**
- Primeira suíte cobrindo `templating.py` + provider factory
- Base para refactor sem medo no futuro

### Sugestão de sequência

1. **Agora:** mergear `fix/models-from-form-data`
2. **Próximo:** reescrever `questions.md` (rápido, fecha frente de prompts)
3. **Depois:** atacar item #4 (re-testar com modelo grande) — valida o trabalho todo
4. **Em seguida:** decidir entre destravar `autonomous_edit.md` (C) ou ir para dívidas técnicas (B)

---

## 📌 Notas finais

- Esta sessão consolidou que **modelos < 13B têm teto cognitivo** para instruções complexas — não é defeito de prompt, é limitação inerente. Mas prompts bem desenhados elevam até esses modelos significativamente.
- A descoberta de que o backend ignorava `config.json` para escolher provider foi o achado mais impactante: desbloqueou testes reais com modelos grandes e validou que vários "defeitos de prompt" eram na verdade limitação do modelo pequeno rodando silenciosamente.
- A arquitetura modular do projeto (definida no `BRIEFING.md`) facilitou todas as refatorações — cada mudança ficou contida no módulo apropriado, sem ondas de impacto cruzado.

🎆 **EXPLOSÃO!**
