# 🐛 Bugs Corrigidos e Pontos de Atenção — Agent AI Megumin

> Documento gerado ao final do bootcamp (15/05/2026).
> Use como contexto inicial ao continuar o desenvolvimento.

---

## Bugs Corrigidos

### Fase 5

- **Tabelas markdown renderizando como texto plano** — corrigido adicionando `remark-gfm` ao `react-markdown`.

### Fase 6

- **Campo Api Key usando `***` como texto editável** em vez de placeholder visual — corrigido separando estado `newApiKey` do valor carregado do backend. Campo começa vazio com placeholder `••••••••`.
- **Botão "Mostrar" revelando `***`** em vez da chave real — corrigido limitando o toggle apenas a chaves digitadas na sessão atual. Chaves já salvas não podem ser reveladas por segurança (o backend nunca as devolve).
- **Emojis nas seções de configurações** — substituídos por ícones lucide-react para consistência visual entre sistemas operacionais.

### Fase 7

- **`LoadingBubble` duplicado durante streaming** — apareciam dois balões simultâneos do Megumin (um com cursor, outro com `...`). Corrigido com flag `isStreaming` que suprime o `LoadingBubble` enquanto o stream está ativo.
- **Cursor de streaming preso indefinidamente** — ocorria quando o evento `done` não era emitido (queda de rede, erro silencioso). Corrigido com limpeza de segurança após o loop que força `isStreaming: false`.
- **Resposta não aparecia após execução de tools** — limitação do Ollama: após tool calling, a resposta volta como bloco único em vez de stream de tokens, então `on_chat_model_stream` não disparava. Corrigido via fallback `on_chain_end + format_response` que emite o texto completo quando nenhum token chegou via streaming.

---

## ⚠️ Pontos que Merecem Atenção

### Personalidade Megumin (limitação de modelo)

Modelos locais testados ignoram instruções de roleplay via system prompt:

| Modelo | Ferramentas | Personalidade |
|--------|-------------|---------------|
| qwen3.5:9b | ✅ Funciona | ⚠️ Parcial |
| llama3.1:8b | ✅ Funciona | ❌ Ignora persona |
| gemma4:e4b | ✅ Funciona | ❌ Ignora persona |

O código de injeção está correto — é limitação dos modelos abaixo de 13B. Para personalidade plena, usar modelos maiores via Ollama ou APIs externas (OpenRouter, Gemini).

### Anúncio antes de escrever (Modo Agente)

O system prompt instrui o agente a anunciar textualmente antes de usar `write_file`, mas modelos pequenos ignoram essa instrução e executam diretamente. Também dependente do modelo — não é bug de código.

### Estilização de tabelas markdown

Funcionam corretamente, mas as bordas estão sutis demais no tema dark. Vale um ajuste visual de polish.

### Dropdown de modelos para APIs externas

Ao trocar para provider OpenAI-compatible, o dropdown não carrega modelos dinamicamente — o usuário precisa digitar o nome manualmente. Cada API tem endpoint diferente para listar modelos, o que tornaria a implementação complexa. Aceitável para o escopo atual.

### `.git` duplicado no setup

O `uv init` criou um `.git` dentro de `backend/` ao inicializar o projeto, gerando um submódulo Git acidental. Foi corrigido manualmente removendo o `.git` filho. Vale documentar no README para quem seguir o projeto do zero.

### `main.py` placeholder gerado pelo `uv`

O `uv init` gerou um `main.py` na raiz de `backend/` junto com o `app/main.py` real. Foi removido, mas é um ponto de confusão para quem inicializa do zero.

### Persistência do histórico de conversas

A memória de sessão é in-memory — reiniciar o backend apaga todo o histórico. Aceitável para o escopo do bootcamp, mas limitante para uso real. Evolução natural: persistir sessões em SQLite ou arquivo JSON.

### Testes automatizados

Apenas a sandbox de segurança (`core/security.py`) tem cobertura de testes. O restante não tem testes automatizados — aceitável pelo escopo, mas seria o próximo passo antes de evoluir o projeto para produção.
