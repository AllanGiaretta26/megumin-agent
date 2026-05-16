"""
Utilitário de templating de prompts.

Permite usar str.format_map em prompts .md sem quebrar quando
um placeholder está ausente — útil para prompts que evoluem
e ganham/perdem variáveis ao longo do tempo.

Uso típico:
    from app.shared.templating import render_template

    template = "Olá {nome}, drama {drama_level}"
    resultado = render_template(template, nome="Megumin", drama_level=70)
"""


class SafeDict(dict):
    """
    Dict que devolve a chave literal entre chaves quando ausente.

    Diferente do dict padrão, não levanta KeyError em format_map —
    deixa o placeholder intacto na string final.

    Exemplo:
        >>> "Olá {nome}, sobra {x}".format_map(SafeDict(nome="Megu"))
        'Olá Megu, sobra {x}'
    """

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_template(template: str, **kwargs) -> str:
    """
    Renderiza um template substituindo {placeholders} pelos kwargs.

    Placeholders sem valor correspondente ficam intactos —
    sem KeyError, sem crash.

    Args:
        template: string com placeholders no formato {nome}.
        **kwargs: valores a serem substituídos.

    Returns:
        String renderizada.
    """
    return template.format_map(SafeDict(**kwargs))
