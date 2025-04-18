def fix_encoding(line):
    """
    Corrige problemas comuns de encoding em uma string.
    """
    try:
        # Corrige strings mal decodificadas (ex: 'jÃ¡ nÃ£o' -> 'já não')
        return line.encode("latin1").decode("utf-8")
    except Exception:
        return line
