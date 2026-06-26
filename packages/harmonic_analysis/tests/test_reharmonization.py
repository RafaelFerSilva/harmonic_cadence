"""Camada 3 — motor de reharmonização."""

from harmonic_analysis.domain.reharmonization import reharmonize_symbols


def _by_technique(suggestions, technique):
    return [s for s in suggestions if s.technique == technique]


def test_tritone_substitution_of_resolving_dominant():
    # G7 resolvendo em C ⇒ sugere Db7, preservando a função dominante.
    sugs = reharmonize_symbols(["G7", "C"], key="C", mode="major")
    tri = _by_technique(sugs, "tritone_substitution")
    assert tri, "esperava uma substituição de trítono"
    s = tri[0]
    assert s.original == ("G7",)
    assert s.result == ("Db7",)
    assert s.function == "D"  # função dominante preservada
    assert "tríton" in s.rationale.lower()


def test_secondary_dominant_inserted_before_target():
    # Dm (ii) precedido por outro acorde ⇒ insere A7 (V7/ii) antes.
    sugs = reharmonize_symbols(["Am", "Dm", "G7", "C"], key="C", mode="major")
    sec = _by_technique(sugs, "secondary_dominant")
    dm = [s for s in sec if s.original == ("Dm",)]
    assert dm, "esperava dominante secundário antes de Dm"
    assert dm[0].result == ("A7", "Dm")
    assert dm[0].operation == "insert_before"


def test_suggestions_are_labeled_and_justified():
    sugs = reharmonize_symbols(["C", "F", "G7", "C"], key="C", mode="major")
    assert sugs
    for s in sugs:
        assert s.technique
        assert s.rationale and len(s.rationale) > 10
        assert s.positions
        assert s.result
        assert s.function in {"T", "SD", "D"}


def test_tritone_sub_preserves_dominant_function_and_target():
    sugs = reharmonize_symbols(["G7", "C"], key="C", mode="major")
    s = _by_technique(sugs, "tritone_substitution")[0]
    assert s.function == "D"
    # Db7 ainda resolve no mesmo alvo (C), por meio-tom descendente.
    assert s.result == ("Db7",)


def test_suggestions_are_ranked_and_deduped():
    sugs = reharmonize_symbols(["C", "F", "G7", "C"], key="C", mode="major")
    ranks = [s.technique for s in sugs]
    # técnicas mais idiomáticas (trítono) aparecem antes das raras (intercâmbio)
    if "tritone_substitution" in ranks and "modal_interchange" in ranks:
        assert ranks.index("tritone_substitution") < ranks.index("modal_interchange")
    # sem duplicatas exatas
    sigs = [(s.technique, s.positions, s.result) for s in sugs]
    assert len(sigs) == len(set(sigs))
