"""Verificador de ADMISSÃO de cifras transcritas da fonte primária (songbook).

Critério (change `ingest-songbook-vols-2-5`, D3): o manifesto `Acordes
Utilizados:` do header — transcrito dos DIAGRAMAS impressos na página do livro,
nunca da própria extração — deve estar coberto pela extração canônica do corpo:
`extract_chords_from_lines(corpo) ⊇ diagramas`, com desconto de dialeto (mesmos
pitch-classes via parse). Reusa o critério do `audit_completeness.py` (o mesmo
oráculo da quarentena, agora preventivo, na entrada).

Saída por arquivo:
  - `FALHA <slug>: faltam [...]` — acorde declarado sem suporte no corpo
    (hipótese nº 1: erro de transcrição). Exit 1: o arquivo NÃO é admitido.
  - `aviso <slug>: extras [...]` — acorde extraído que não está no manifesto
    (typo provável na transcrição, ou diagrama omitido pelo livro — revisar).
    Não bloqueia sozinho, mas exige olhar antes de fechar o lote.
  - `ok <slug>` — verificado.

Uso:  uv run python scripts/verify_transcription.py cifras/novo1.md [novo2.md ...]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_completeness import _CODE, _MAN, _TICK, _pcs, audit_manifest  # noqa: E402

from cifra_core import cifra_from_text, extract_chords_from_lines  # noqa: E402


def _extras(path: str) -> list[str]:
    """Acordes extraídos do corpo que não estão no manifesto (pós-dialeto)."""
    text = open(path, encoding="utf-8").read()
    m = _MAN.search(text)
    if not m:
        return []
    declared = set(_TICK.findall(m.group(1)))
    body = "\n".join(_CODE.findall(text)) or text
    extracted = set(
        extract_chords_from_lines(
            cifra_from_text(body).cifra, known_chords=frozenset(declared)
        )
    )
    declared_pcs = {_pcs(s) for s in declared} - {None}
    return sorted(
        s for s in extracted - declared
        if _pcs(s) is not None and _pcs(s) not in declared_pcs
    )


def main() -> int:
    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        return 2
    for p in paths:
        if not os.path.exists(p):
            print(f"FALHA {p}: arquivo não existe")
            return 1
        text = open(p, encoding="utf-8").read()
        if not _MAN.search(text):
            print(f"FALHA {os.path.basename(p)[:-3]}: sem manifesto "
                  f"`Acordes Utilizados:` (admissão exige o oráculo)")
            return 1

    missing = audit_manifest(sorted(paths))
    rc = 0
    for p in sorted(paths):
        slug = os.path.basename(p)[:-3]
        if slug in missing:
            print(f"FALHA {slug}: faltam {missing[slug]}")
            rc = 1
            continue
        extras = _extras(p)
        if extras:
            print(f"aviso {slug}: extras {extras} (revisar transcrição/diagramas)")
        else:
            print(f"ok {slug}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
