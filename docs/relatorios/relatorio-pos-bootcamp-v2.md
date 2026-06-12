# 📋 Relatório Pós-Bootcamp v2 — Refactor de Prompts e Calibração

> **Período coberto:** 17/05/2026 (sessão única de continuação)
> **Foco:** Correção de framing entre prompts, calibração de drama via tiers e few-shots estruturados, completação do módulo de prompts.
> **Continuação de:** [`relatorio-pos-bootcamp-v1.md`](relatorio-pos-bootcamp-v1.md) (v1)

---

## 📑 Índice

1. [Resumo executivo](#1-resumo-executivo)
2. [Linha do tempo](#2-linha-do-tempo)
3. [Branches criadas](#3-branches-criadas)
4. [Passo 2 — Refactor de prompts e correção de framing](#4-passo-2--refactor-de-prompts-e-correção-de-framing)
5. [Passo 3 — Calibração de drama + sistema de tiers + few-shots estruturados](#5-passo-3--calibração-de-drama--sistema-de-tiers--few-shots-estruturados)
6. [Passo 4 — Completação do questions.md](#6-passo-4--completação-do-questionsmd)
7. [Aprendizados arquiteturais](#7-aprendizados-arquiteturais)
8. [Limitações conhecidas (dívida explícita)](#8-limitações-conhecidas-dívida-explícita)
9. [Dívidas técnicas atualizadas](#9-dívidas-técnicas-atualizadas)
10. [Onde paramos](#10-onde-paramos)
11. [Próximos passos](#11-próximos-passos)

---

## 1. Resumo executivo

A v2 deu sequência ao trabalho do relatório v1 atacando três frentes específicas que sobraram ou regrediram depois da última merge: **conflito de framing entre o `personality.md` e os prompts de modo com estrutura rígida**, **calibração da escala de drama** (especialmente a faixa 70, que vinha rendendo intensidade próxima de 100), e **completação do `questions.md`** com formato padronizado de citação e snippets.

A vitória mais limpa foi a **eliminação de vazamentos Megumin em `drama_level = 0`**: a auditoria estática dos 4 prompts de modo encontrou um few-shot dramático em `agent.md` (path traversal em voz Megumin), um few-shot dramático em `questions.md` (seção "Nota de Personalidade" duplicando o controle do `drama_level`) e o `free_chat.md` inteiro escrito em voz Megumin. Os três foram corrigidos. Hoje, em `drama_level = 0`, o agente responde 100% neutro.

A limitação mais grave é a **credibilidade do sistema de tiers**. Anotamos `(N+)` em cada bordão do vocabulário canônico ("EXPLOSÃO!!!" → tier 76+, "Eis-me aqui!" → tier 51+, etc.) na intenção de oferecer controle granular sobre o que cada faixa de drama pode dizer. Smoke tests com `gpt-oss:120b` confirmaram que o tier é **prescrição textual sujeita a vazamento** — `"mortal"` (tier 76+) apareceu em `drama_level = 70` mesmo após a recalibração. Modelos pequenos (8B-9B) interpolam a partir das demonstrações que veem (few-shots), não da especificação que leem. O tier serve como guia para o autor do prompt, não como controle determinístico do output.

A dívida principal que esta fase **não tocou**: `autonomous_edit.md` continua bloqueado pela decisão arquitetural sobre confirmação interativa (mesma situação registrada no v1, item 7.4).

---

## 2. Linha do tempo

### Passo 1 — Sessão inicial pós-merge

- Mini smoke test informal com `qwen3.5:9b` local + `gpt-oss:120b` (Ollama Cloud) revelou 3 regressões persistentes do conjunto recém-merged:
  1. `drama_level = 70` produzindo intensidade próxima de 100
  2. Planning sem H3 e sem checklist no topo
  3. Agent composto silencioso (zero anúncio, zero plano, zero resumo)
- Decisão: atacar em sequência, com checkpoints e diagnóstico antes de cada patch.

### Passo 2 — Refactor de prompts e correção de framing

- **Diagnóstico (Checkpoint 2A):** mapeamento estático dos 4 prompts de modo + `personality.md` apontou conflito direto entre a posição da personality (`graph.py:54` concatena `personality + "\n\n" + mode.system_prompt` — personality primeiro) e a estrutura exigida pelos modos. A Regra #5 do personality cobria apenas "Modo Estudo / Modo Dúvidas: clareza antes do drama", omitindo Agente e Planejamento.
- **Reescrita da Regra #5** do `personality.md` para cobrir os 4 modos com guidance específico (Agente: drama no anúncio e resumo, nunca entre tool calls; Planejamento: drama na intro e conclusão, nunca no corpo; Dúvidas: drama ao redor de citações; Conversa Livre: livre).
- **Adição de "Tarefas compostas" no `agent.md`** (Abordagem A: plano no início + execução em lote + resumo final), com critério de detecção (3+ operações de arquivo relacionadas). Resolveu contradição residual reescrevendo Restrição inquebrável #5 ("Um arquivo por vez **em tarefas atômicas**...").
- **Neutralização do exemplo de path traversal** no `agent.md` (removeu *"Os arcanos recusaram esta invocação"* — único few-shot Megumin do arquivo).
- **Remoção da "Nota de Personalidade"** do `questions.md` (duplicava controle de drama e tinha few-shot dramático embutido).
- **Reescrita completa do `free_chat.md`** (Opção A — modo neutro), preservando estrutura, domínios, regras de safety e formato; removendo todas as declarações Megumin, os 4 few-shots em voz Megumin e a referência a "personality (definida acima) segue ativa".

### Mini smoke test pós-Passo 2

- `drama_level = 0`: ✅ neutro em todos os modos (vazamento fechado).
- `drama_level = 70`: ⚠️ ainda em ~90.
- Planning: ⚠️ ainda sem H3 nem checklist.
- Agent composto: ❌ continua silencioso.

### Passo 3 — Calibração + tiers + few-shots estruturados

- **Diagnóstico (Checkpoint 3A):** auditoria dos few-shots do `personality.md` revelou que dos 5 existentes (0/30/70/100 + tsundere 70), **zero** demonstravam convivência com estrutura rígida. Também: o few-shot de `drama_level = 70` continha *"Clã Crimson Demon"*, expressão que a própria descrição textual da faixa 76-100 reserva para si. Modelo aprende pelo exemplo, não pela descrição.
- **Recalibração do few-shot drama=70** ("for em Python"): de 6 marcadores Megumin para 2 leves ("Ah", "elegante", "direto"). Removidas todas as referências tier 76+.
- **Sistema de tiers `(N+)`** nos bordões da seção "Vocabulário canônico". Mapeamento alinhado às descrições textuais das faixas: entry/execution e tsundere = (51+); auto-apresentação, "EXPLOSÃO!!!", "Clã Crimson Demon", "mortal" (endereçamento), "magia uma vez por dia" = (76+). Legenda de 3 linhas explicando o que `(N+)` significa.
- **Few-shot novo: planning estruturado em drama=70** (~50 linhas). Demonstra Checklist no topo + 4 passos como H3 + `**Por quê:**` / `**Como validar:**` em linhas próprias + bloco "Riscos / Pontos de atenção". Drama em 2 linhas (intro e conclusão), zero no corpo.
- **Few-shot novo: agent composto em drama=70**. Demonstra anúncio do plano com lista dos arquivos + 3 tool calls `write_file` em sequência sem prosa entre elas + resumo final. Usa a mesma notação de tool call do `agent.md` (`[chama \`write_file(...)\`]` fora do blockquote) para reforçar o padrão entre os dois arquivos.

### Mini smoke test pós-Passo 3

- Caso 1 (`drama_level = 70`, Conversa Livre, "API REST em 1 frase"): ❌ vazamento — `"mortal"` (tier 76+) apareceu.
- Caso 4 (`drama_level = 70`, Planejamento, endpoint REST): ⚠️ parcial — modelo herdou seções (Resumo, Premissas, Riscos) e labels (`**Por quê:**` / `**Como validar:**`), mas perdeu H3 e checklist.
- Caso 5 (`drama_level = 70`, Agente composto, "calculadora científica"): ⚠️ parcial — modelo sabe o padrão (cobrança resgata resposta correta), mas não aciona na primeira tentativa.
- Score: 0/3 vitórias claras, 2/3 melhorias parciais, 1/3 regressão persistente.
- **Decisão consciente:** aceitar estado parcial; iterações no `personality.md` estavam dando retorno decrescente.

### Passo 4 — Completação do questions.md

- **Frente 1:** seção `## Formato de citação` — formato `caminho/arquivo.ext:linha`, exemplo de linha única e range, regra de caminho relativo.
- **Frente 2:** seção `## Quando incluir snippets` — 3 critérios de inclusão, 3 de exclusão, template de snippet com comentário de citação na primeira linha. Bloco de código em markdown plain (fora de blockquote) por lição direta do Caso 4 do Passo 3 (marcadores estruturais buried em blockquote são ignorados pelo modelo).
- **Frente 3:** padronização `Você → Tu` em todas as 6 linhas originais (alinhamento com `agent.md`, `planning.md`, `free_chat.md` reescrito, `personality.md`).
- **Frente 4 (verificação anti-regressão):** confirmado que arquivo não menciona personagem, não tem "Nota de Personalidade", não menciona `drama_level`. Alinhado com Regra #5 do `personality.md` ("Modo Dúvidas: citações no formato `arquivo:linha` e snippets de código são literais").
- Smoke test não-bloqueante validou as duas frentes principais (citação no formato correto, snippet com comentário de citação).

---

## 3. Branches criadas

| Branch | Status | Conteúdo |
|---|---|---|
| `main` (commits diretos) | ✅ Aplicado | Passos 2 e 3 (3+1 commits): personality #5, agent.md composite tasks + path traversal, questions+free_chat neutrality, tier system + few-shots estruturados. Decisão consciente de commitar direto em `main` em vez de abrir branch (Passos pequenos, escopo conhecido). |
| `refactor/questions-prompt` | ✅ Pronta para PR | Passo 4 — formato de citação, snippets, padronização Tu. Único commit isolado, pronto para abrir PR contra `main`. |

> O `.gitignore` ganhou uma entrada `docs/` no meio do caminho (commit `54d39b9` na main) para que documentação interna como este relatório fique local-only.

---

## 4. Passo 2 — Refactor de prompts e correção de framing

### Causa-raiz diagnosticada

O `personality.md` (~125 linhas) é concatenado **antes** do prompt do modo (`graph.py:54`, comentário explícito: *"modelos 8B-9B ancoram identidade no primeiro parágrafo do system prompt"*). Os 4 few-shots originais do personality eram todos prosa fluida. Os prompts de modo com estrutura rígida (planning com H3 + checklist; agent com Regra dos 3 Passos + Tarefas compostas) chegavam **depois** de 125 linhas de incentivo para escrever prosa solta. O modelo herdava o tom da personality e dropava a estrutura.

A Regra #5 do `personality.md` mencionava apenas "Modo Estudo / Modo Dúvidas: clareza antes do drama", sem cobertura para Agente, Planejamento ou (depois da renomeação) Conversa Livre. Os modos com estrutura rígida ficavam sem salvaguarda explícita contra a pressão da prosa teatral instalada pelos few-shots.

### Soluções aplicadas

- **Regra #5 reescrita** como guia mode-aware: cita os 4 modos pelo nome e diz onde drama é permitido em cada um. Fecha com *"Quando o modo exige estrutura, **estrutura vence**. Personalidade vive nas dobras da estrutura, não em vez dela."*
- **Seção "Tarefas compostas"** adicionada ao `agent.md` formalizando o batch flow (anúncio inicial → tool calls em sequência → resumo final). Critério de detecção textual: 3+ operações de arquivo, palavras-chave como "projeto", "estrutura", "scaffolding".
- **Restrição inquebrável #5 do `agent.md`** reescrita: *"Um arquivo por vez em tarefas atômicas — não agrupes várias escritas sem anúncios individuais. Em tarefas compostas (3+ operações), segue o formato em lote descrito acima."* Resolveu a contradição que a nova seção introduzia.
- **Exemplo de path traversal** no `agent.md` neutralizado (de *"Os arcanos recusaram esta invocação..."* para *"A ferramenta `read_file` retornou erro de sandbox..."*). Era o único few-shot em voz Megumin do arquivo, e em `drama_level = 0` ele era o único modelo que o agente tinha para erros de sandbox.
- **"Nota de Personalidade" removida** do `questions.md`. A seção duplicava o controle de `drama_level` (que vive no `graph.py`, não no prompt do modo) e tinha few-shot dramático embutido (*"Vasculhei os arcanos do projeto e encontrei..."*).
- **Reescrita completa do `free_chat.md`** em modo neutro (Opção A escolhida sobre B "manter como está" e C "patch híbrido"). Estrutura preservada one-for-one (9 seções, 4 domínios, 3 situações de incerteza, 3 formatos por tipo, escala de comprimento, 5 restrições). Voz trocada de "és uma arquimaga formada nos arcanos da Academia de Axel" para "Tu cobres bem programação e tecnologia". 4 few-shots reescritos preservando propósito didático: lista virou "prateleira numerada" em vez de "pergaminho de feitiços"; pizza perdeu "guerra arcana"; sensível ("sintomas estranhos") perdeu "esta arquimaga domina feitiços de código"; incerteza ("copa 2002") perdeu "Se os meus arcanos não traíram". A personality, quando `drama > 0`, redramatiza por cima.

### Resultado mensurado

`drama_level = 0` ficou efetivamente neutro nos 4 modos. Nas faixas `drama > 0` os ganhos foram parciais — diagnosticados no Passo 3 como problema de **falta de demonstração**, não de **descrição insuficiente**.

---

## 5. Passo 3 — Calibração de drama + sistema de tiers + few-shots estruturados

### Diagnóstico (Checkpoint 3A)

Mapeamento estático de **gradação atual** revelou três coisas:

1. **Saltos não-lineares entre faixas.** Análise por contagem de marcadores Megumin nos few-shots da mesma pergunta:
   - drama=30 → 1 marcador ("elegância")
   - drama=70 → 6 marcadores ("Eis", "feitiço", "invocas", "canaliza", "cadência arcana", "Clã Crimson Demon")
   - drama=100 → 8 marcadores
   - Salto 30→70 (+500%) é 15× maior do que 70→100 (+33%).

2. **Vazamento de tier no few-shot drama=70.** *"Clã Crimson Demon"* aparece no few-shot de drama=70, mas a descrição textual da faixa 76-100 explicitamente reserva essa referência para si. Few-shot venceu descrição.

3. **Zero few-shots demonstram estrutura.** Os 5 existentes (0/30/70/100 + tsundere=70) são 100% prosa. Não há um único exemplo de H3 numerado, checklist, lista numerada, anúncio de tool call, tabela, ou seções estruturadas separadas. O modelo nunca viu "manter personalidade dentro de estrutura" — só viu "personalidade = prosa solta".

### Soluções aplicadas

- **Recalibração do few-shot drama=70** ("for em Python") — de 6 marcadores Megumin para 2 leves (`"Ah"`, `"elegante"`, `"direto"`). Removidas: `"feitiço"`, `"invocas"`, `"canaliza"`, `"cadência arcana"`, `"Clã Crimson Demon"`. Conteúdo técnico preservado.
- **Sistema de tiers** — adicionada anotação `(N+)` em cada bordão do "Vocabulário canônico":

  | Tier | Exemplos |
  |---|---|
  | (51+) | "Eis-me aqui!", "Canalizando os arcanos...", "Contemplai esta obra arcana!", tsundere "C-como ousas?!", "Hmpf!" |
  | (76+) | "Meu nome é Megumin!", "Arquimaga do Clã Crimson Demon, ao teu dispor!", "EXPLOSÃO!!!", "Eis a tua resposta, mortal.", "Esta foi a minha magia definitiva do dia." |

  Adicionada legenda de 3 linhas explicando `(N+)` = "disponível a partir de `drama_level = N`".

- **Few-shot novo: drama=70 modo Planejamento** (Sub-tarefa 3.3). Resposta a *"Adicione um endpoint `GET /users`..."*. 4 passos como H3, com `**Por quê:**` e `**Como validar:**` em linhas próprias, Checklist no topo, bloco "Riscos / Pontos de atenção" no final. Drama em 2 linhas (intro `"Eis-me aqui — o pergaminho será desenrolado."` e conclusão `"Eis o plano — pronto para a execução."`). Bordões dentro do tier permitido (apenas 51+).

- **Few-shot novo: drama=70 modo Agente composto** (Sub-tarefa 3.4). Resposta a *"Crie um pacote `utils/` com `strings.py`, `dates.py` e `__init__.py`."*. Anúncio do plano com lista dos 3 arquivos → 3 tool calls `write_file` em sequência separadas por linha em branco, **sem prosa entre elas** → resumo final em 1 linha. Notação de tool call (`[chama \`write_file("path", "content")\`]`) idêntica à usada no `agent.md` para reforçar a mesma forma nos dois arquivos.

### Smoke test do Passo 3 (3.5)

Rodado pelo usuário com `gpt-oss:120b` via Ollama Cloud:

| Caso | Configuração | Resultado |
|---|---|---|
| 1 | drama=70, free_chat, "API REST em 1 frase" | ❌ FALHA — `"mortal"` (tier 76+) vazou |
| 4 | drama=70, planning, endpoint GET /chat/sessions | ⚠️ PARCIAL — herdou seções e labels, perdeu H3 e checklist |
| 5 | drama=70, agent, "calculadora científica" | ⚠️ PARCIAL — silêncio na 1ª tentativa, padrão correto após cobrança |

### Decisão de aceitar estado parcial

- O `personality.md` está substancialmente melhor que antes (vazamento de Crimson Demon na faixa 70 sumiu, sistema de tiers oferece guia explícito mesmo que imperfeito).
- Retorno decrescente em cada nova iteração.
- As 3 regressões restantes são tratáveis em frentes específicas (validação com modelo maior, recalibração do few-shot drama=100, ou redesenho do few-shot de planning fora do blockquote).
- Risco subestimado registrado: **credibilidade do tier system** — ele é prescrição textual, não controle determinístico. Documentado na seção [Limitações conhecidas](#8-limitações-conhecidas-dívida-explícita).

---

## 6. Passo 4 — Completação do questions.md

### Estado anterior

Arquivo de 6 linhas, "Você é um assistente para responder dúvidas sobre o projeto atual..." — minimal stub. Auditoria pós-bootcamp deu 4/5: faltavam formato padronizado de citação e regras claras sobre snippets de código.

### Mudanças aplicadas

- **`## Formato de citação`** — formato `caminho/arquivo.ext:linha` com exemplos de linha única (`app/modules/agent/graph.py:47`) e range (`:47-52`). Exceção para arquivos sem linha específica (`pyproject.toml` sozinho). Regra explícita: caminho relativo à raiz, nunca absoluto.

- **`## Quando incluir snippets`** — 3 critérios de inclusão (perguntas sobre "como algo funciona" com 3-15 linhas relevantes, função/classe/bloco específico, pedido explícito de "mostrar"), 3 de exclusão (arquitetura geral, snippets > 20 linhas, código trivial pelo nome). Template de snippet com comentário de citação na primeira linha. **Bloco de código em markdown plain**, fora de blockquote — lição direta do Caso 4 do Passo 3, onde marcadores estruturais buried em blockquote eram descartados pelo modelo.

- **Padronização `Você → Tu`** — substituição literal palavra por palavra das 6 linhas originais. Alinhamento com `agent.md`, `planning.md`, `free_chat.md` reescrito, `personality.md`. Imperativos negativos viraram subjuntivo em tu ("Não escrevas, cries ou modifiques") como já é o padrão em `agent.md` ("Nunca chames", "Nunca sobrescrevas").

### Verificação anti-regressão (Frente 4)

- Sem menção a personagem (Megumin, arquimaga, arcano).
- Sem "Nota de Personalidade" (já tinha sido removida no Passo 2).
- Sem menção a `drama_level`.
- Alinhado com Regra #5 do `personality.md` (que promete *"Modo Dúvidas: citações no formato `arquivo:linha` e snippets de código são literais"*).

Arquivo cresceu 6 → 45 linhas. Todo o crescimento é especificação que estava faltando, não fluff.

---

## 7. Aprendizados arquiteturais

Esta seção consolida insights que emergiram da análise do Checkpoint 3.5 (smoke test final do Passo 3) e da auditoria do Passo 2. Cada insight tem implicação prática para iterações futuras de prompt.

### 7.1 Few-shots vencem regras textuais em modelos pequenos (8B-9B)

- **Onde surgiu:** Checkpoint 3A. Dos 5 few-shots do `personality.md`, 0 demonstravam estrutura formal. A Regra #5 do personality (reescrita no Passo 2) tem instrução textual correta — *"estrutura vence; personalidade vive nas dobras"* — mas modelos 8B-9B continuavam dropando H3/checklist mesmo lendo essa regra.
- **Implicação:** ao introduzir regra crítica em prompt, **sempre** acompanhar com pelo menos 1 few-shot demonstrando a regra em ação. Instrução sem demonstração tem efetividade próxima de zero abaixo de 13B.

### 7.2 Marcadores estruturais (H3, checklist) ficam invisíveis dentro de blockquote

- **Onde surgiu:** smoke test 3.5 Caso 4. O few-shot novo do Passo 3 (planning estruturado) estava todo dentro de blockquote (`>` no início de cada linha). O modelo herdou os marcadores textuais (`**Por quê:**`, `**Como validar:**`, seção "Riscos") porque aparecem como prosa dentro do blockquote. Mas perdeu H3 (`### Passo N`) e checklist (`- [ ]`) porque esses são marcadores estruturais que o modelo aprende como "elemento do exemplo isolado", não como "estrutura a replicar".
- **Implicação:** few-shots que demonstram estrutura formal ou ficam **fora de blockquote**, ou são **duplicados** (uma vez dentro de blockquote como demonstração + uma vez fora como template canônico). Esta lição foi aplicada imediatamente no Passo 4: os blocos de código `python` do `questions.md` ficaram em markdown plain, não em blockquote.

### 7.3 ReAct tem fase de exploração antes do "início da resposta"

- **Onde surgiu:** smoke test 3.5 Caso 5. Agent composto chamou 4 tools (`list_directory` + 2× `read_file` + `write_file`) silenciosamente antes de "começar a resposta". A regra "Anúncio do plano — no início da resposta" assumia que "início da resposta" é antes de qualquer tool, mas na prática o agente entrou em fase de exploração ReAct antes, e ao chegar no momento de escrever já tinha esquecido de anunciar.
- **Implicação:** prompts de agente precisam distinguir explicitamente entre (a) anúncio inicial obrigatório **antes de qualquer tool**, mesmo as de exploração, e (b) execução em lote depois. A formulação atual ("anuncie no início da resposta") é ambígua para o ciclo ReAct.

### 7.4 Few-shot mais expressivo domina o resto da escala

- **Onde surgiu:** análise final do Passo 3. O few-shot drama=100 contém 6 marcadores tier 76+ simultaneamente (EXPLOSÃO + Yunyun + mortal + Contemplai + Eis + Ah ha ha). Em drama=70, o modelo interpola entre o few-shot recalibrado de drama=70 (2 marcadores leves) e o few-shot de drama=100 (6 marcadores tier 76+). Resultado: drama=70 puxa 3-4 marcadores tier 76+ em perguntas que não bateram com o few-shot recalibrado.
- **Implicação:** calibrar **toda a escala**, não só a faixa "problemática". Se a faixa âncora (drama=100) está saturada, todas as faixas abaixo herdam parte dessa saturação por interpolação.

### 7.5 Tier annotation é prescrição textual, não garantia

- **Onde surgiu:** smoke test 3.5 Caso 1. `"mortal"` (tier 76+) apareceu em drama=70 mesmo após a recalibração da 3.2 e mesmo com a anotação `(76+)` explícita no vocabulário canônico.
- **Implicação:** o sistema de tiers serve como **documentação interna** (autor do prompt sabe quais palavras pertencem a qual nível) e como **prescrição** que melhora aderência marginalmente, mas **não é mecanismo de controle determinístico** sobre o output do modelo. Documentar isso visivelmente para evitar que contribuidores futuros assumam que basta "adicionar tier" para fechar uma classe de vazamento.

---

## 8. Limitações conhecidas (dívida explícita)

### 8.1 Tier system não é garantia

Os tiers `(1+)`, `(26+)`, `(51+)`, `(76+)` em `personality.md` são prescrição textual sujeita a vazamento, especialmente em modelos abaixo de 13B (e, como vimos com `gpt-oss:120b`, também acima — embora com frequência menor).

**Vazamentos observados:**
- `"mortal"` (tier 76+) apareceu em `drama_level = 70` no smoke test 3.5 Caso 1, com `gpt-oss:120b`.

**Não fazer:**
- Confiar nos tiers como controle de saída.
- Assumir que adicionar tier resolve vazamento.

**Fazer:**
- Tratar tier como guia para o autor do prompt.
- Validar via smoke test toda vez que adicionar bordões novos ou recalibrar faixas.
- Considerar recalibrar a faixa-âncora (drama=100) também — não só a faixa intermediária problemática.

### 8.2 Regressões aceitas conscientemente no Passo 3

1. **drama=70 ainda vaza vocabulário tier 76+ ocasionalmente** (smoke test 3.5 Caso 1).
2. **Planejamento usa numeração inline em vez de H3 + checklist no topo** (Caso 4). Modelo herdou as seções e labels do few-shot, mas perdeu os marcadores estruturais por estarem buried em blockquote.
3. **Agent composto silencia na primeira tentativa para pedidos exploratórios** (Caso 5). Modelo sabe o padrão — cobrança resgata o anúncio + lote + resumo —, mas não aciona sozinho quando o pedido exige exploração prévia (ReAct loop).

**Hipótese da causa-raiz comum:** modelos abaixo de 13B (e parcialmente acima) não seguem regras textuais sem demonstração concreta. Próximo experimento natural: retestar com modelo maior (Claude Sonnet via openai_compat ou outro 70B+) para validar se a limitação é do **design dos prompts** ou do **tamanho do modelo**. Esse experimento muda a priorização do resto do roadmap.

---

## 9. Dívidas técnicas atualizadas

Itens novos desta fase + itens herdados do v1 ainda em aberto.

| # | Item | Origem | Esforço | Prioridade |
|---|---|---|---|---|
| 1 | `temperature` da config não chega ao LLM | v1 | Baixo | Média |
| 2 | Hidratação de tool calls no histórico | v1 | Médio | Média |
| 4 | Re-testar prompts com modelo grande (≥ 30B) | v1 | Baixo | **Alta** (valida design de tudo) |
| 10 | Confirmação interativa no Modo Agente (destrava `autonomous_edit.md`) | v1 | Alto | Média |
| 16 | Validar tier system com modelo grande — confirmar se tier vaza menos ou igual | v2 | Baixo | Alta (continua #4) |
| 17 | Considerar recalibrar few-shot drama=100 para reduzir saturação (lição 7.4) | v2 | Baixo | Média |
| 18 | Testar few-shot estruturado fora de blockquote (lição 7.2) | v2 | Baixo | Média |
| 19 | Documentar no `agent.md` distinção entre "anúncio antes de qualquer tool" vs "anúncio no início da resposta" (lição 7.3) | v2 | Baixo | Média |
| 20 | `personality.md:122` corrigido nesta fase (era item #3 do v1) — ✅ resolvido junto da Regra #5 | v1 → fechado | — | — |

Itens v1 com prioridade ≤ Baixa preservados sem mudança: #5 (acessibilidade), #6 (`on_event` deprecado), #7 (label "Megumin" quando drama=0), #8 (heurística frágil de status), #9 (`astream` sem Pydantic), #11 (persistência de sessões), #12 (testes automatizados), #13 (`build_system_prompt()` pura), #14 (modo avançado dropdown), #15 (502 intermitente).

---

## 10. Onde paramos

### Estado do roadmap de prompts

| # | Prompt | Status v1 | Status v2 |
|---|---|---|---|
| 1 | `personality.md` | ✅ Reescrito e validado | ✅ Regra #5 mode-aware + tiers + 2 few-shots estruturados (com limitações registradas) |
| 2 | `agent.md` | ✅ Reescrito e validado | ✅ + seção "Tarefas compostas" + path traversal neutralizado + Restrição #5 ajustada |
| 3 | `free_chat.md` | ✅ Renomeado e expandido | ✅ Reescrito Opção A (neutro — drama 100% via personality) |
| 4 | `autonomous_edit.md` | ❌ Bloqueado | ❌ **Continua bloqueado** (sem decisão sobre confirmação interativa) |
| 5 | `planning.md` | ✅ Reescrito (v2) | ✅ Sem mudanças nesta fase |
| 6 | `questions.md` | ❌ Pendente | ✅ Citação + snippets + Tu form |

### Branches abertas

- `refactor/questions-prompt` — pronta para PR contra `main` (Passo 4, 1 commit isolado).

### Configuração funcional usada nos smoke tests

- Provider: `openai_compatible`
- Modelo: `gpt-oss:120b` (Ollama Cloud)
- Base URL: `https://ollama.com/v1`
- API key: configurada
- Personalidade: `drama_level = 70` (faixa testada), `temperature = 0.9`, `language = pt-BR`
- Project path: configurado em projeto de teste separado

---

## 11. Próximos passos

Sequência sugerida, em ordem de leverage decrescente:

1. **Retestar com modelo grande externo (Claude Sonnet via openai_compat, ou outro 70B+)** — alavancagem mais alta. Todas as 3 regressões do Passo 3 são consistentes com "modelo pequeno não segue regra textual". Se um modelo grande seguir os tiers corretamente e respeitar H3, então o design dos prompts está correto e a frente vira UX (banner avisando "drama_level pleno requer modelo X+"), não mais iteração de prompt. Se um modelo grande **também** falhar, o design está errado e mais iteração em `personality.md` é trabalho perdido. Esse experimento **muda o roteiro do resto do roadmap**.

2. **Item #1 — temperature da config não chega ao LLM.** Baixo custo, pode dar ganho marginal em aderência estrutural (temperature mais baixa = mais determinístico). Vale tentar antes de mais iteração em prompt.

3. **Item #2 — hidratação de tool calls no histórico.** Depende de decisão UX (mostrar `[chama write_file...]` literal no chat ou renderizar como card?). Não atacar sem essa decisão.

4. **`autonomous_edit.md`** — continua bloqueado por decisão arquitetural sobre confirmação interativa. Não destravar sem decidir primeiro.

5. **Recalibrar few-shot drama=100** (item #17) — se a decisão for continuar iterando `personality.md` em vez de migrar para modelo maior.

---

## 📌 Notas finais

- A v2 reforçou a regra de ouro do v1: **modelos < 13B têm teto cognitivo para instruções complexas**, e mesmo modelos 70B+ não tratam regras textuais como controle determinístico. Few-shot demonstrando vence regra descrita.
- O ganho mais concreto da v2 foi a eliminação completa de vazamentos Megumin em `drama_level = 0`: o agente hoje é capaz de responder 100% neutro quando configurado para isso. Antes da v2, a faixa 0 tinha vazamentos consistentes vindos dos próprios prompts de modo.
- A v2 documentou **três frentes específicas onde a iteração em prompt tem retorno decrescente** (Limitações 8.2) — explicitar a dívida evita ciclos de iteração improdutivos no futuro.
- O sistema de tiers é uma decisão de design com **trade-off explícito**: oferece linguagem comum para discutir o que cada faixa pode dizer, mas exige disciplina do autor para não confundir com controle determinístico. Vale manter exatamente por isso.
