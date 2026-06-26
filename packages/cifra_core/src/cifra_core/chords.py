import re
from typing import List


class ChordPattern:
    """
    Regex canônico para detectar/extrair símbolos de acorde em texto.

    Cobre cifras como: C, Am7, G/B, F#m7b5, Bb7(9), E7M(9).
    """

    CHORD = re.compile(
        r"([A-G][#b]?"                       # fundamental (com # ou b)
        r"(?:"                               # pilha de qualidades/extensões
        r"maj|min|sus|dim|aug|add|7M|m|M|°"  # qualidades (7M = maj7, notação BR)
        r"|6|7|9|11|13|4|2"                  # extensões
        r"|[#b](?:5|9|11|13)"               # alterações (b5, #5, b9, #11, ...)
        r"|\([^)]*\)"                        # tensões entre parênteses
        r")*"
        r"(?:/[A-G][#b]?)?)"                # baixo invertido
    )

    @classmethod
    def find_all(cls, text: str) -> List[str]:
        """Encontra todos os acordes em um texto."""
        return cls.CHORD.findall(text)
