from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# TypedDict define um dicionário com chaves e tipos fixos.
# É como um DTO/record do Java, mas sem precisar de classe — o LangGraph
# usa esse "pacote de dados" para passar informação entre os nós do grafo.
class AgentState(TypedDict):
    # add_messages é um reducer: em vez de substituir a lista de mensagens,
    # ele ACUMULA as novas mensagens no final. Isso é essencial para o loop
    # ReAct — cada nó adiciona sua mensagem sem precisar copiar a lista inteira.
    messages: Annotated[list, add_messages]
    session_id: str
    response: str          # resposta final extraída pelo nó format_response
    mode: str              # "study" | "questions" | "planning" | "agent" | "autonomous_edit"
    project_path: str      # caminho da sandbox; "" quando o modo não exige (nunca None —
                           # InjectedState nas tools espera str, não str|None)
    allowed_tools: list[str]  # nomes das tools que o modo atual pode usar
    system_prompt: str        # carregado do .md pelo nó select_mode; não entra em messages
    drama_level: int          # 0–100, lido da config em runtime; injetado no personality.md
    language: str             # idioma de resposta (ex: "pt-BR"), lido da config; injetado no personality.md
