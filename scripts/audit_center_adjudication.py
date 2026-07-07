"""Auditoria anti-drift da worklist de centro adjudicada.

Re-deriva as músicas com divergência de centro (`center_status='diverge'`) da
extração CORRENTE (a `v_song_current` do `corpus.duckdb`) e compara, por `slug`,
com o corpus curado `harmonic_analysis.corpus.tonal_center_adjudications`. Reporta
drift nas DUAS direções e **falha** (código não-zero) se houver qualquer um:

  - música `diverge` SEM veredito (pendente de adjudicação);
  - veredito ÓRFÃO (para música que não diverge mais — o motor evoluiu).

Imprime a contagem por `winner` (denominador visível, nunca placar). NUNCA altera o
corpus (o curador decide). Sem `corpus.duckdb`, avisa e sai 0.

Uso:  uv run python scripts/audit_center_adjudication.py [corpus.duckdb]
"""

import os
import sys
from collections import Counter

import duckdb
from cifra_core.slug import slugify

from harmonic_analysis.corpus.tonal_center_adjudications import ADJUDICATIONS

_DIVERGE_SQL = """
SELECT slug FROM v_song_current WHERE center_status = 'diverge' ORDER BY slug
"""


def diverge_slugs(db_path: str) -> set[str]:
    con = duckdb.connect(db_path, read_only=True)
    try:
        rows = con.execute(_DIVERGE_SQL).fetchall()
    finally:
        con.close()
    return {slugify(r[0]) for r in rows}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    db_path = args[0] if args else "corpus.duckdb"
    if not os.path.exists(db_path):
        print(f"Aviso: {db_path} ausente — rode `harmonic corpus build` primeiro.")
        return 0

    diverge = diverge_slugs(db_path)
    curated = {a.key: a for a in ADJUDICATIONS}

    drift = 0
    print(f"\nAuditoria anti-drift da worklist de centro ({db_path}):")
    print(f"  músicas 'diverge' no corpus corrente: {len(diverge)}")
    print(f"  vereditos curados:                    {len(curated)}")

    for slug in sorted(diverge - curated.keys()):
        drift += 1
        print(f"  [SEM VEREDITO] {slug} — adjudicar")

    for slug in sorted(curated.keys() - diverge):
        drift += 1
        print(f"  [VEREDITO ÓRFÃO] {slug} — não diverge mais")

    if drift == 0:
        counts = Counter(a.winner for a in ADJUDICATIONS)
        print("  worklist × corpus: SEM drift.")
        print("  distribuição por winner:")
        for kind, n in sorted(counts.items()):
            print(f"    {kind:16s} {n}")
    else:
        print(f"  DRIFT: {drift} discrepância(s) — corpus e worklist fora de sincronia.")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
