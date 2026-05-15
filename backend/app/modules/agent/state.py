from typing import TypedDict

# TypedDict define um dicionário com chaves e tipos fixos.
# É como um DTO/record do Java, mas sem precisar de classe — o LangGraph
# usa esse "pacote de dados" para passar informação entre os nós do grafo.
class AgentState(TypedDict):
    messages: list   # histórico completo da conversa (objetos LangChain)
    session_id: str  # identifica a sessão do usuário
    response: str    # resposta final a ser devolvida ao caller
