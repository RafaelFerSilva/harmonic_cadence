"""Baseline funcional sobre o songbook — Chediak é a base, o Cifra Club não entra.

Corpus = cifras LOCAIS (`cifras/*.md`, gitignored), ingeridas pelo caminho do
`local-chord-input` (`cifra_from_text`) — NUNCA scraping, NUNCA `cc_key`. O ouro nasce da
música + Chediak:

1. **Centro funcional** (Chediak pp.84/87): `chediak_functional_center` ENCONTRA a tônica
   pela resolução do dominante funcional ancorada num repouso estrutural (first/last). A
   métrica mede se o `detect_key` CONCORDA com esse centro, sobre o subconjunto onde o
   critério dispara; o resto fica em quarentena (cobertura honesta).
2. **Invariante funcional** (transposição-invariante): todo trítono real
   (`Category.DOMINANT`) deve ser lido como DOMINANTE na análise — nunca como empréstimo
   ou subdominante. Violações são defeitos funcionais.

A tonalidade absoluta é só quadro de exibição: a leitura funcional é invariante a
transposição.

Uso:  uv run python scripts/songbook_baseline.py   (offline; precisa de cifras/)
"""

import glob
import os
import re

from cifra_core import ChordPattern, cifra_from_text

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.services.analysis_service import AnalysisService
from harmonic_analysis.validation import chediak_functional_center

_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_CODE = re.compile(r"```(.*?)```", re.S)


def _chords_from_md(path: str) -> list[str]:
    """Extrai os símbolos de acorde do bloco de cifra do .md (via local-chord-input)."""
    text = open(path, encoding="utf-8").read()
    blocks = _CODE.findall(text)
    body = "\n".join(blocks) if blocks else text
    cifra = cifra_from_text(body)
    return [s for line in cifra.cifra for s in ChordPattern.find_all(line) if s]


def _dominant_invariant(chords: list[str], analysis: dict) -> list[str]:
    """Defeitos: trítono real (Category.DOMINANT) NÃO lido como dominante na análise."""
    items = analysis.get("harmonic_analysis") or []
    violations = []
    for item, sym in zip(items, chords):
        try:
            is_tritone_dom = Chord(sym).get_category().value == "dominant"
        except Exception:
            continue
        if is_tritone_dom:
            code = (item.get("function_code") or "").upper()
            # códigos dominantes do projeto: D, D2 (ii cad.), Dsec, Daux, Dext, SubV...
            if not any(k in code for k in ("D", "SUBV")):
                violations.append(f"{sym}→{item.get('function_code')}")
    return violations


def main() -> None:
    paths = sorted(glob.glob("cifras/*.md"))
    if not paths:
        print("Nenhuma cifra em cifras/ (corpus local ausente).")
        return

    service = AnalysisService()  # sem provider: caminho local
    agree = disagree = quarantine = 0
    worklist: list[str] = []
    defects: list[str] = []
    n = 0
    for path in paths:
        name = os.path.basename(path)[:-3]
        chords = _chords_from_md(path)
        if not chords:
            continue
        n += 1
        est = detect_key(chords)
        det = (est.tonic_pc, est.mode) if est else None
        center = chediak_functional_center(chords)

        # Centro = CORROBORAÇÃO de dois métodos independentes (detect_key × critério
        # funcional do Chediak), NÃO acurácia: o achador funcional sem anotação é heurístico.
        if center is None:
            quarantine += 1
        elif det == center:
            agree += 1
        else:
            disagree += 1
            d = f"{_PC[det[0]]} {det[1]}" if det else "—"
            worklist.append(
                f"  {name[:26]:<27} detect_key={d:<9} funcional={_PC[center[0]]} {center[1]}"
            )

        # Invariante funcional (independe do centro — a parte rochosa, Chediak-pura).
        result = service.analyze_song_data_structured(
            {"artist": "", "name": name, "cifra": [" ".join(chords)]}
        )
        if "error" not in result:
            v = _dominant_invariant(chords, result)
            if v:
                defects.append(f"  {name[:26]:<27} {', '.join(v[:4])}")

    print(f"\nBaseline FUNCIONAL sobre o songbook (corpus local, n={n}) — base = Chediak\n")
    print("INVARIANTE funcional (a base: trítono real ⇒ dominante; transposição-invariante):")
    print(f"  músicas sem defeito: {n - len(defects)}/{n}")
    if defects:
        print("  defeitos (trítono não lido como dominante):")
        print("\n".join(defects))

    covered = agree + disagree
    print("\nCentro tonal — CORROBORAÇÃO (detect_key × critério funcional do Chediak), NÃO acurácia:")
    print(f"  cobertura (critério funcional disparou): {covered}/{n}  (quarentena: {quarantine})")
    if covered:
        print(f"  concordam (centro de alta confiança):    {agree}/{covered}  ({agree/covered:.0%})")
    if worklist:
        print("\n  worklist de curadoria (os dois métodos divergem — Chediak adjudica):")
        print("\n".join(worklist))


if __name__ == "__main__":
    main()
