import os
from pathlib import Path

from app.core.exceptions import PathTraversalError


def validate_path(requested: str, project_path: str) -> Path:
    """Resolve o caminho solicitado e garante que está dentro de project_path.

    Path traversal é uma classe de ataque onde o código malicioso usa sequências
    como "../" para escapar do diretório permitido e acessar arquivos sensíveis
    do sistema operacional. Exemplos de ataques que esta função bloqueia:
      - "../../etc/passwd"           → sobe dois níveis e acessa /etc/passwd
      - "/etc/passwd"                → caminho absoluto fora do projeto
      - "subdir/../../outro/arquivo" → combinação de subdir + traversal

    A defesa correta é resolver ambos os caminhos para absolutos (.resolve())
    ANTES de comparar — isso elimina qualquer "../" ou link simbólico.

    Args:
        requested: Caminho relativo ou absoluto fornecido pelo LLM.
        project_path: Diretório raiz da sandbox (vem do estado do agente).

    Returns:
        Path absoluto e seguro dentro de project_path.

    Raises:
        PathTraversalError: Se o caminho resolvido sair de project_path.
    """
    anchor = Path(project_path).resolve()
    # Trata caminhos absolutos e relativos uniformemente
    if Path(requested).is_absolute():
        target = Path(requested).resolve()
    else:
        target = (anchor / requested).resolve()

    # Compara com os.sep no final para evitar falso positivo de prefixo de nome.
    # Ex: anchor=/tmp/proj, target=/tmp/project → startswith sem sep passaria, com sep bloqueia.
    if not str(target).startswith(str(anchor) + os.sep) and target != anchor:
        raise PathTraversalError(
            f"Acesso negado: '{requested}' está fora do project_path permitido."
        )

    return target
