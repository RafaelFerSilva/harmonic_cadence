import re
from typing import List


class ChordPattern:
    """
    Regex canônico para detectar/extrair símbolos de acorde em texto.

    Cobre cifras como: C, Am7, G/B, F#m7b5, Bb7(9), E7M(9).
    """

    CHORD = re.compile(
        r"([A-G][#b]?"                          # fundamental (com # ou b)
        r"(?:"                                  # pilha de qualidades/extensões
        r"maj|min|sus|dim|aug|add|alt|7M|m|M|°|º"  # qualidades (7M = maj7, BR)
        r"|11|13|[245679]"                      # extensões (5 = power chord)
        r"|[#b](?:5|9|11|13)"                  # alterações #/b (b5, #5, #11, ...)
        r"|(?:5|9|11|13|2)[+-]"                # alterações ± (5+, 9-, 13-, Cifra Club)
        r"|/[#b]?\d+"                          # tom acrescentado por barra (6/9)
        r"|\([^)]*\)"                           # tensões entre parênteses
        r"|\+"                                  # tríade aumentada (C+)
        r")*"
        r"(?:/[A-G][#b]?)?)"                   # baixo invertido (nota)
    )

    @classmethod
    def find_all(cls, text: str) -> List[str]:
        """Encontra todos os acordes em um texto."""
        return cls.CHORD.findall(text)
