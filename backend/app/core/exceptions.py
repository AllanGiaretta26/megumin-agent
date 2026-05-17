class OllamaUnavailableError(Exception):
    """Levantada quando o serviço Ollama não pode ser alcançado."""


class PathTraversalError(Exception):
    """Levantada quando um path ultrapassa o project_path permitido."""


class SessionNotFoundError(Exception):
    """Levantada quando session_id não existe na memória."""


class ModeNotFoundError(Exception):
    """Levantada quando o nome do modo não é reconhecido pelo sistema."""


class ModelListError(Exception):
    """Levantada quando não é possível listar modelos do provider configurado."""
