"""Ingestão de cifra a partir de texto local (`cifra_from_text`).

Converte texto cru no mesmo `Cifra` normalizado do provider, reusando
`clean_cifra_lines` (uma vez, idempotente). Sem tom da fonte (`key=""`).
"""

from cifra_core import Cifra, cifra_from_text, clean_cifra_lines


def test_preserves_chord_lines():
    c = cifra_from_text("C  Am  Dm  G7\nC  Am  Dm  G7  C")
    assert isinstance(c, Cifra)
    assert "C  Am  Dm  G7" in c.cifra
    assert c.cifra[-1].strip().endswith("C")


def test_has_no_source_key():
    # A fuga da armadilha dos metadados: sem "Tom:" — a tonalidade nasce do detect_key.
    assert cifra_from_text("C F G7 C").key == ""


def test_identity_defaults_and_overrides():
    assert cifra_from_text("C G7 C").artist == ""
    assert cifra_from_text("C G7 C").name == ""
    c = cifra_from_text("C G7 C", artist="Eu", title="Minha Prog")
    assert c.artist == "Eu" and c.name == "Minha Prog"


def test_empty_text_yields_empty_cifra():
    c = cifra_from_text("")
    assert c.cifra == () and c.is_empty


def test_filtering_is_idempotent_with_clean_cifra_lines():
    raw = "Intro\nC  Am  Dm  G7\n\n\nC  Am  Dm  G7  C\n"
    once = cifra_from_text(raw).cifra
    # Reaplicar o filtro canônico não muda nada (contrato "filtra uma vez").
    assert list(once) == clean_cifra_lines(list(once))


def test_chord_extraction_is_not_done_here():
    # A ingestão produz LINHAS limpas, não acordes — extração é do motor (ChordPattern).
    c = cifra_from_text("C  Am  Dm  G7")
    assert c.cifra == ("C  Am  Dm  G7",)  # linha inteira, não tokens de acorde
