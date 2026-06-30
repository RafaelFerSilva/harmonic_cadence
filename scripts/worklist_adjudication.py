"""Instrumentação READ-ONLY da worklist de corroboração (#7) — não altera o motor.

Para cada música onde `detect_key` × `chediak_functional_center` DIVERGEM, classifica a
divergência pela RELAÇÃO HARMÔNICA entre os dois centros (paralela, relativa, V↔I, IV↔I,
trítono, outra) e expõe as pistas estruturais (1º/último acorde = repousos, símbolo do
dominante que ancorou o centro funcional). Saída = tabela de adjudicação para cruzar com o
Chediak — o livro adjudica, este script só ORGANIZA o desacordo.

Reusa os MESMOS dois métodos do baseline (`detect_key`, `chediak_functional_center`) e a
MESMA extração de acordes do `songbook_baseline.py`. Nada de `cc_key`, nada de scraping.

Uso:  uv run python scripts/worklist_adjudication.py
"""

import glob
import os
import re

from cifra_core import cifra_from_text, extract_chords_from_lines
from cifra_core.theory.chord_parse import parse

from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.validation import chediak_functional_center

_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_CODE = re.compile(r"```(.*?)```", re.S)
_MANIFEST = re.compile(r"\*\*Acordes Utilizados:\*\*\s*(.+)")
_TICK = re.compile(r"`([^`]+)`")


def _manifest(text: str) -> frozenset[str]:
    m = _MANIFEST.search(text)
    return frozenset(_TICK.findall(m.group(1))) if m else frozenset()


def _chords_from_md(path: str) -> list[str]:
    text = open(path, encoding="utf-8").read()
    blocks = _CODE.findall(text)
    body = "\n".join(blocks) if blocks else text
    cifra = cifra_from_text(body)
    return extract_chords_from_lines(cifra.cifra, known_chords=_manifest(text))


def _relacao(det_root: int, det_mode: str, fun_root: int, fun_mode: str) -> str:
    """Nomeia a relação harmônica det→funcional (intervalo do funcional p/ o detect_key).

    Convenção: o centro FUNCIONAL (Chediak, resolução do dominante) é o referencial; o
    rótulo descreve o que o `detect_key` escolheu RELATIVO a ele.
    """
    iv = (det_root - fun_root) % 12
    if iv == 0:
        return "paralela (mesma fundamental, modo trocado)"
    # relativa: maior↔menor com fundamentais a uma 3ªm (rel. menor = +9; rel. maior = +3)
    if det_mode != fun_mode:
        if iv == 9 and fun_mode == "major" and det_mode == "minor":
            return "relativa (detect pegou a relativa menor)"
        if iv == 3 and fun_mode == "minor" and det_mode == "major":
            return "relativa (detect pegou a relativa maior)"
    if iv == 7:
        return "V↔I (detect pegou o V — dominante como tônica)"
    if iv == 5:
        return "IV↔I (detect a 4ªJ acima — funcional pegou o V?)"
    if iv == 6:
        return "trítono"
    if iv == 2:
        return "2ªM acima"
    if iv == 10:
        return "2ªM abaixo"
    return f"outra (+{iv} semitons)"


def _ancora(chords: list[str], fun_root: int) -> str:
    """O par dominante→tônica que ANCOROU o centro funcional (V7 5ªJ ou SubV7 ½t acima)."""
    dom, subv = (fun_root + 7) % 12, (fun_root + 1) % 12
    parsed = []
    for s in chords:
        try:
            p = parse(s)
            parsed.append((s, p.root.pitch_class, (p.bass or p.root).pitch_class,
                           (p.category() if callable(p.category) else p.category).value))
        except Exception:
            parsed.append((s, None, None, ""))
    for i in range(len(parsed) - 1):
        sym, root, _, cat = parsed[i]
        if cat == "dominant" and root in (dom, subv) and parsed[i + 1][2] == fun_root:
            tipo = "V7" if root == dom else "SubV7"
            return f"{sym}({tipo})→{parsed[i + 1][0]}"
    return "—"


def main() -> None:
    paths = sorted(glob.glob("cifras/*.md"))
    rows = []
    clusters: dict[str, int] = {}
    for path in paths:
        name = os.path.basename(path)[:-3]
        chords = _chords_from_md(path)
        if not chords:
            continue
        est = detect_key(chords)
        det = (est.tonic_pc, est.mode) if est else None
        center = chediak_functional_center(chords)
        if center is None or det is None or det == center:
            continue
        rel = _relacao(det[0], det[1], center[0], center[1])
        bucket = rel.split(" ")[0]
        clusters[bucket] = clusters.get(bucket, 0) + 1
        rows.append({
            "name": name,
            "det": f"{_PC[det[0]]} {det[1]}",
            "fun": f"{_PC[center[0]]} {center[1]}",
            "rel": rel,
            "first": chords[0],
            "last": chords[-1],
            "ancora": _ancora(chords, center[0]),
        })

    rows.sort(key=lambda r: r["rel"])
    print(f"\nWorklist de corroboração — {len(rows)} divergências (READ-ONLY, motor intacto)\n")
    print("Clusters por relação harmônica (centro FUNCIONAL = referencial):")
    for k, v in sorted(clusters.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>2}  {k}")

    print("\n| música | detect_key | funcional (Chediak) | relação | 1º | último | âncora V→I |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['name']} | {r['det']} | {r['fun']} | {r['rel']} "
              f"| `{r['first']}` | `{r['last']}` | `{r['ancora']}` |")

    print("\nLeitura: 'paralela'/'relativa' = concordam na REGIÃO (baixo risco, desempate de "
          "modo/relativa);\n'V↔I'/'IV↔I' = ambiguidade dominante-como-tônica (o gate funcional "
          "deveria mediar).\nCada linha é um item p/ o Chediak adjudicar — o livro decide, não "
          "o detector.")


if __name__ == "__main__":
    main()
