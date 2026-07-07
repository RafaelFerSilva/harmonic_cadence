"""Auditoria anti-drift do ledger de trítono adjudicado.

Re-deriva as ocorrências do ledger de trítono não-dominante da extração CORRENTE
(a view `v_ledger_tritone_nondominant` do `corpus.duckdb`, que é a saída
materializada do motor) e compara, por chave `(slug, position)`, com o corpus
curado `harmonic_analysis.corpus.tritone_adjudications`. Reporta drift nas DUAS
direções e **falha** (código não-zero) se houver qualquer um:

  - ocorrência do ledger SEM veredito (pendente de adjudicação);
  - veredito ÓRFÃO (para ocorrência que não está mais no ledger — extração mudou).

Imprime a contagem por veredito (denominador visível, nunca placar). NUNCA altera o
corpus (o curador decide). Sem `corpus.duckdb`, avisa e sai 0.

Uso:  uv run python scripts/audit_tritone_adjudication.py [corpus.duckdb]
"""

import os
import sys
from collections import Counter

import duckdb
from cifra_core.slug import slugify

from harmonic_analysis.corpus.tritone_adjudications import ADJUDICATIONS

_LEDGER_SQL = """
select s.slug, l.position, l.symbol
from v_ledger_tritone_nondominant l
join v_song_current s on s.song_id = l.song_id
order by s.slug, l.position
"""


def ledger_keys(db_path: str) -> dict[tuple[str, int], str]:
    """(slug, position) → symbol para cada ocorrência do ledger corrente."""
    con = duckdb.connect(db_path, read_only=True)
    try:
        rows = con.execute(_LEDGER_SQL).fetchall()
    finally:
        con.close()
    return {(slugify(slug), int(pos)): sym for slug, pos, sym in rows}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    db_path = args[0] if args else "corpus.duckdb"
    if not os.path.exists(db_path):
        print(f"Aviso: {db_path} ausente — rode `harmonic corpus build` primeiro.")
        return 0

    led = ledger_keys(db_path)
    curated = {a.key: a for a in ADJUDICATIONS}

    drift = 0
    print(f"\nAuditoria anti-drift do ledger de trítono ({db_path}):")
    print(f"  ocorrências no ledger corrente: {len(led)}")
    print(f"  vereditos curados:              {len(curated)}")

    pending = sorted(k for k in led if k not in curated)
    for slug, pos in pending:
        drift += 1
        print(f"  [SEM VEREDITO] {slug} pos={pos} ({led[(slug, pos)]}) — adjudicar")

    orphans = sorted(k for k in curated if k not in led)
    for slug, pos in orphans:
        drift += 1
        print(f"  [VEREDITO ÓRFÃO] {slug} pos={pos} — não está mais no ledger")

    if drift == 0:
        counts = Counter(a.verdict for a in ADJUDICATIONS)
        print("  ledger × corpus: SEM drift.")
        print("  distribuição por veredito:")
        for kind, n in sorted(counts.items()):
            print(f"    {kind:20s} {n}")
    else:
        print(f"  DRIFT: {drift} discrepância(s) — corpus e ledger fora de sincronia.")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
