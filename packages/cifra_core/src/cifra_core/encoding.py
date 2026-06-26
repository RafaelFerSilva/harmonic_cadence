def fix_encoding(line: str) -> str:
    """
    Corrige problemas comuns de encoding em uma string.

    Texto UTF-8 mal-decodificado como latin1 (mojibake, ex.: 'jÃ¡ nÃ£o')
    é recuperado; texto já correto ou indecodificável é devolvido intacto.
    """
    try:
        return line.encode("latin1").decode("utf-8")
    except Exception:
        return line
