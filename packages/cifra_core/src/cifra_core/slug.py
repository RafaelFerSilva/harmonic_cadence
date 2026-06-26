import re
import unicodedata


def slugify(text: str) -> str:
    """
    Converte um nome de artista/música para o slug usado em URLs e no cache.

    Remove acentos, descarta caracteres especiais (mantendo hífens), passa
    para minúsculas e une as palavras com hífen. Determinística.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text)
    words = text.lower().split()
    return "-".join(words)
