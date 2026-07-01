"""Classificação de linha por densidade (sanitize-chord-extraction, Fase 1).

A linha é a unidade de desambiguação cifra-vs-letra: uma palavra de letra pode parecer
acorde (`Brasil`→`B`), então quem decide é a densidade de acordes válidos da LINHA, não o
token isolado.
"""

import pytest

from cifra_core import (
    LineKind,
    classify_line,
    clean_cifra_lines,
    extract_chords_from_lines,
    is_chord_token,
    malformed_chord_token,
)


@pytest.mark.parametrize(
    "line",
    [
        "C / / G / Am",
        "Bm7      E7(b9)    Am7 /",
        "Fm7      Bb7(9)   Eb7M     Eb6      Am7   D7(9) G6 /",
        "Introdução: Dm7 G7 Dm7 G7",  # rótulo + acordes -> classifica o resto
    ],
)
def test_chord_lines_classified_chord(line):
    assert classify_line(line) is LineKind.CHORD


@pytest.mark.parametrize(
    "line",
    [
        "Com seu passado E tradição",
        "É livre e é feliz E tem tudo o que quis ...",
        "Salve as belezas Desse meu Brasil Com seu passado E tra",
        "Feio não é bonito O morro existe Mas pede pra se acabar",
    ],
)
def test_lyric_lines_classified_lyric(line):
    assert classify_line(line) is LineKind.LYRIC


def test_bare_section_label_is_section():
    assert classify_line("Introdução:") is LineKind.SECTION


def test_is_chord_token_fullmatch_rejects_prose():
    # casa o acorde inteiro
    for s in ("C", "Am7", "G/B", "C6/9", "D7(9)", "F#m7b5"):
        assert is_chord_token(s)
    # palavra de letra cuja inicial é nota: prefixo casa, token inteiro NÃO
    for w in ("Brasil", "Com", "Feio", "Desse"):
        assert not is_chord_token(w)


def test_extraction_reads_only_chord_lines():
    lines = [
        "Dm7      G7        C7M",          # CHORD
        "É só isso o meu baião E não tem",  # LYRIC -> 0 tokens
        "Bm7 E7(b9) Am7",                   # CHORD
    ]
    syms = extract_chords_from_lines(lines)
    assert syms == ["Dm7", "G7", "C7M", "Bm7", "E7(b9)", "Am7"]
    assert "E" not in syms  # o "E" de "E não tem" não vaza (linha LYRIC)


def test_extraction_drops_phantom_single_letters_from_prose():
    # linha de prosa cuja densidade é baixa -> nenhum token sai
    lines = ["Salve as belezas Desse meu Brasil Com seu passado E tradição"]
    assert extract_chords_from_lines(lines) == []


def test_ambiguous_bare_token_gated_by_whitelist():
    # tríade nua 'A' numa linha CHORD: sem whitelist sai; com whitelist sem 'A' some
    line = ["A / / D / / E /"]
    assert extract_chords_from_lines(line) == ["A", "D", "E"]
    assert extract_chords_from_lines(line, known_chords={"D", "E"}) == ["D", "E"]
    # token NÃO-ambíguo (com extensão) passa independentemente da whitelist
    assert extract_chords_from_lines(["A7 / D7M /"], known_chords=set()) == ["A7", "D7M"]


# --- Notação malformada (report-unidentified-notations) ---


@pytest.mark.parametrize("tok", ["D9/S", "C9/S", "Db9/S", "C7(b13"])
def test_malformed_chord_token_true(tok):
    # prefixo de acorde válido + resto '/'/'(' inválido + resíduo com lixo
    assert malformed_chord_token(tok) is True


@pytest.mark.parametrize(
    "tok",
    [
        "Am7/",                    # acorde + barra de compasso final (só decoração)
        "A7(b9)/",                 # idem com tensão
        "Bb7(9)///",               # múltiplas barras
        "B°/A/",                   # baixo válido + barra
        "Gm7(11)///Gb7(#11)///",   # DOIS acordes colados por barra (resíduo vazio)
        "Brasil",                  # palavra de letra (resto não começa com '/'/'(' )
        "Em",                      # acorde completo
        "A7(b9)",                  # acorde completo
    ],
)
def test_malformed_chord_token_false(tok):
    assert malformed_chord_token(tok) is False


def test_malformed_line_stays_chord_and_recovers_valid_chords():
    # A linha dominada por 'D9/S' NÃO some (vira CHORD); os acordes válidos são recuperados.
    line = "D9/S / E/D / D9/S / D7(9) / D9/S"
    assert classify_line(line) is LineKind.CHORD
    unident: list[str] = []
    syms = extract_chords_from_lines([line], unidentified=unident)
    assert "E/D" in syms and "D7(9)" in syms       # válidos recuperados
    assert "D9" not in syms                          # o prefixo do malformado NÃO é chutado
    assert unident.count("D9/S") == 3                # cada malformado coletado


def test_glued_chords_by_bar_separator_are_both_extracted():
    # dois acordes colados por barra, numa linha CHORD (contexto de densidade real)
    unident: list[str] = []
    line = "C7(9) / Gm7(11)///Gb7(#11)/// F7M /"
    assert classify_line(line) is LineKind.CHORD
    syms = extract_chords_from_lines([line], unidentified=unident)
    assert "Gm7(11)" in syms and "Gb7(#11)" in syms  # ambos extraídos
    assert unident == []                              # nenhum reportado como malformado


def test_classification_does_not_mutate_line_stream():
    # A classificação é leitura pura; clean_cifra_lines segue idempotente e preservando letra.
    lines = ["Dm7 G7 C7M", "Bim bom bim bom o meu baião", "Am7 D7 G"]
    cleaned = clean_cifra_lines(lines)
    assert clean_cifra_lines(cleaned) == cleaned  # idempotente
    assert "Bim bom bim bom o meu baião" in cleaned  # letra preservada para display
