import re


def format_name(text: str) -> str:
    """
    Remove hífens, substitui por espaço e capitaliza cada palavra.
    Exemplo: 'tom-jobim' -> 'Tom Jobim'
    """
    if not isinstance(text, str):
        return text
    # Remove hífens e underscores, substitui por espaço
    text = re.sub(r"[-_]+", " ", text)
    # Remove espaços duplicados
    text = re.sub(r"\s+", " ", text)
    # Capitaliza cada palavra
    return text.title().strip()
