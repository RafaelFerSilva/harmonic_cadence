"""classify-special-function-dominants — Chediak XXXIV(a), pp.112-113 + quadro.

Resolução precede empréstimo (bVII7 em tom menor); II7 = subdominante alterada;
VII7 sem resolução no I = V7/III; invariante que trava a isenção de Emp no ledger."""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis

C = HarmonicAnalysis("C", "major")
Am = HarmonicAnalysis("A", "minor")


def _fn(H, sym, nxt=None):
    return H.analyze_function(
        Chord(sym), None, Chord(nxt) if nxt else None, False, False
    )


def test_bvii7_resolving_diatonic_fourth_is_dsec_in_minor():
    """Em Lá menor, G7 (bVII7) → C (III diatônico) é V7/III — resolução precede
    empréstimo (Chediak p.114, ex. Bb7→Eb)."""
    code, name, _ = _fn(Am, "G7", "C7M")
    assert code == "Dsec" and "V7/" in name


def test_bvii7_backdoor_stays_emp_in_major():
    """Em Dó maior, Bb7 → C (baixo sobe um tom) segue Emp/AEM (p.112(1))."""
    code, _, desc = _fn(C, "Bb7", "C7M")
    assert code == "Emp" and "p.112" in desc


def test_bvi7_stays_emp_with_citation():
    code, name, desc = _fn(C, "Ab7", "C7M")
    assert code == "Emp" and "bVI7" in name and "p.113" in desc


def test_ii7_is_altered_subdominant():
    """D7 em Dó sem casar ramo dominante → SD 'Subdominante alterada (II7)'."""
    code, name, desc = _fn(C, "D7", "C7M")
    assert code == "SD" and "II7" in name and "p.113" in desc


def test_ii7_with_functional_resolution_stays_dsec():
    """D7 → G7M (4ªJ diatônica) segue V7/V — a resolução vence."""
    code, name, _ = _fn(C, "D7", "G7M")
    assert code == "Dsec" and "deceptivo" not in name


def test_vii7_to_tonic_stays_cadential():
    code, name, _ = _fn(C, "B7", "C7M")
    assert code == "D" and "cadencial" in name


def test_vii7_without_tonic_resolution_is_v7_of_iii():
    """B7 → F7M (nem I nem III): V7/III deceptivo (p.112(2)/p.114)."""
    code, name, _ = _fn(C, "B7", "F7M")
    assert code == "Dsec" and "V7/III" in name


def test_blues_and_deceptive_branches_untouched():
    assert _fn(C, "C7", "F7")[0] == "T"      # I7 blues
    assert _fn(C, "F7", "C7")[0] == "SD"     # IV7 blues
    assert _fn(C, "A7", "C7M")[0] == "Dsec"  # 0f deceptivo VI7
    assert _fn(C, "Db7", "C7M")[0] == "SubV"  # bII7


def test_emp_dominant_quality_positions():
    """Mapeia onde o coder emite `Emp` p/ dominante-7 (trava a isenção do ledger,
    D4): a CASCATA só o faz em bVII (10) e bVI (8); o único vazamento é o bV7
    (6, `Gb7` em Dó) via leitura genérica de empréstimo FORA da cascata — por
    isso a isenção do ledger filtra por raiz∈{10,8}, não por código cru."""
    from cifra_core.theory import Note

    roots = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    emp_positions = set()
    for root in roots:
        for nxt in (None, "C7M"):
            if _fn(C, f"{root}7", nxt)[0] == "Emp":
                emp_positions.add(
                    (Note.parse(root).pitch_class - Note.parse("C").pitch_class) % 12
                )
    assert emp_positions <= {10, 8, 6}, emp_positions
    assert {10, 8} <= emp_positions  # bVII7/bVI7 seguem Emp (funções especiais)
