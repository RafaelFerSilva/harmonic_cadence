"""Auditoria de completude do corpus — verifica o ledger curado contra a evidência.

Re-deriva, com a extração CORRENTE, o vocabulário declarado × extraído de cada
cifra local (manifesto `Acordes Utilizados` do arquivo e, quando a fonte v4
estiver presente, o header `Acordes:` do livro), descontando dialeto (mesmos
pitch-classes via parse) e mojibake (`FO`≈`F°`). Compara com
`harmonic_analysis.corpus.completeness` e reporta drift nas DUAS direções:

  - entrada curada SEM suporte na auditoria (a extração melhorou → re-curar);
  - divergência auditada SEM entrada no ledger (candidato novo → curar).

NUNCA altera o ledger (o curador decide). Ferramenta local: sem `cifras/`,
avisa e sai 0.

Uso:  uv run python scripts/audit_completeness.py [--v4 songbook-v4-v2.md]
"""

import glob
import os
import re
import sys

from cifra_core import cifra_from_text, extract_chords_from_lines
from cifra_core.slug import slugify
from cifra_core.theory import parse as parse_chord

from harmonic_analysis.corpus.completeness import COMPLETENESS_LEDGER

_MAN = re.compile(r"\*\*Acordes Utilizados:\*\*\s*(.+)")
_TICK = re.compile(r"`([^`]+)`")
_CODE = re.compile(r"```(.*?)```", re.S)
_SONG = re.compile(r"^### (.+?)\n(.*?)(?=^### |\Z)", re.M | re.S)
_FENCE = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)
_AC = re.compile(r"\*\*Acordes:\*\*\s*\n(.+?)(?:\n\s*\n|\n```)", re.S)
_NUM = re.compile(r"^\d+\.\s*")
_SYM = re.compile(r"[A-G][#b]?[^\s|]*")


def _pcs(sym: str):
    """(root_pc, pitch-classes) do símbolo, tolerando mojibake `O`≈`°`; None se não parseia."""
    for cand in (sym, sym.replace("O", "°").replace("º", "°")):
        try:
            p = parse_chord(cand)
            return (p.root.pitch_class, p.pitch_classes())
        except Exception:
            continue
    return None


def _really_missing(declared: set[str], body: str, present_syms: set[str]) -> list[str]:
    """Declarados ausentes do corpo, pós-desconto: substring, dialeto (pitch-classes)."""
    present_pcs = {_pcs(s) for s in present_syms} - {None}
    out = []
    for c in sorted(declared):
        if c in body:
            continue
        cp = _pcs(c)
        if cp is not None and cp in present_pcs:
            continue
        out.append(c)
    return out


def audit_manifest(paths: list[str]) -> dict[str, list[str]]:
    """slug → declarados-ausentes (manifesto do arquivo × extração corrente)."""
    found: dict[str, list[str]] = {}
    for path in paths:
        text = open(path, encoding="utf-8").read()
        m = _MAN.search(text)
        if not m:
            continue
        declared = set(_TICK.findall(m.group(1)))
        body = "\n".join(_CODE.findall(text)) or text
        extracted = set(
            extract_chords_from_lines(
                cifra_from_text(body).cifra, known_chords=frozenset(declared)
            )
        )
        missing = _really_missing(declared - extracted, body, extracted)
        if missing:
            found[os.path.basename(path)[:-3]] = missing
    return found


def audit_v4(src: str) -> dict[str, list[str]]:
    """slug → declarados-ausentes (header `Acordes:` do livro × corpo do fence)."""
    text = open(src, encoding="utf-8").read()
    found: dict[str, list[str]] = {}
    for title, body in _SONG.findall(text):
        title = _NUM.sub("", title.strip())
        mf, md = _FENCE.search(body), _AC.search(body)
        if not (mf and md):
            continue
        block = mf.group(1)
        declared = {
            c.strip() for c in md.group(1).replace("\n", " ").split(",") if c.strip()
        }
        missing = _really_missing(declared, block, set(_SYM.findall(block)))
        if missing:
            found[slugify(title)] = missing
    return found


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    v4 = None
    if "--v4" in sys.argv:
        v4 = sys.argv[sys.argv.index("--v4") + 1]
    elif os.path.exists("songbook-v4-v2.md"):
        v4 = "songbook-v4-v2.md"

    paths = sorted(glob.glob(args[0] if args else "cifras/*.md"))
    if not paths:
        print("Aviso: sem cifras/ locais — auditoria não se aplica aqui.")
        return 0

    audited: dict[str, set[str]] = {}
    for slug, miss in audit_manifest(paths).items():
        audited.setdefault(slug, set()).update(miss)
    if v4 and os.path.exists(v4):
        for slug, miss in audit_v4(v4).items():
            audited.setdefault(slug, set()).update(miss)
    else:
        print("Aviso: fonte v4 ausente — só o oráculo do manifesto foi auditado.")

    drift = 0
    print(f"\nAuditoria de completude (extração corrente, n={len(paths)}):")
    print(f"  divergências auditadas: {len(audited)} músicas")
    for slug, fact in sorted(COMPLETENESS_LEDGER.items()):
        got = audited.get(slug, set())
        if not got:
            drift += 1
            print(f"  [LEDGER SEM SUPORTE] {slug}: curado "
                  f"{list(fact.missing_declared)} mas a auditoria não acha nada "
                  f"(extração melhorou? re-curar)")
    for slug, miss in sorted(audited.items()):
        if slug not in COMPLETENESS_LEDGER:
            drift += 1
            print(f"  [SEM ENTRADA NO LEDGER] {slug}: auditoria acha {sorted(miss)} "
                  f"(candidato a curar)")
    if drift == 0:
        print("  ledger × auditoria: SEM drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
