"""Camada C — retrieval de similaridade harmônica por música.

Fixture inline: materializa músicas, constrói fingerprints por música do banco e
valida a spec `harmonic-similarity-retrieval`:
- embedding é transposição-invariante (mesma sequência de função, tons diferentes → sim 1.0);
- vizinhos materializados são top-K, sem auto-vizinho, ordenados, determinísticos;
- a materialização NÃO altera tabelas-base nem gates (descritivo);
- resolução de slug (existente/inexistente).
"""

import textwrap

import pytest

from harmonic_analysis.overlay.similarity import (
    build_neighbors,
    fingerprint_from_db,
    neighbors_up_to_date,
    resolve_slug,
)
from harmonic_analysis.domain.style_fingerprint import similarity
from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus

# Duas músicas com o MESMO ii-V-I em tons diferentes (C e D) → mesma sequência de
# função → embeddings idênticos. Uma terceira, distinta (só tônica/subdominante).
_FIXTURES = {
    "iivi-em-do": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Dm7` `G7` `C7M`

        ```
        Dm7 G7 C7M
        Dm7 G7 C7M
        ```
        """
    ),
    "iivi-em-re": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Em7` `A7` `D7M`

        ```
        Em7 A7 D7M
        Em7 A7 D7M
        ```
        """
    ),
    "so-tonica-sub": textwrap.dedent(
        """\
        **Acordes Utilizados:** `C7M` `F7M`

        ```
        C7M F7M C7M F7M
        ```
        """
    ),
}


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("similarity")
    cifras = tmp / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(body, encoding="utf-8")
    c = init_db(str(tmp / "c.duckdb"))
    summary = build_corpus(c, str(cifras / "*.md"))
    assert not summary.get("error")
    return c


def _id(conn, slug):
    return resolve_slug(conn, slug)


def test_fingerprint_is_per_song(conn):
    fp = fingerprint_from_db(conn, _id(conn, "iivi-em-do"))
    assert fp.song_count == 1
    assert abs(sum(fp.function_distribution.values()) - 1.0) < 1e-9


def test_transposition_invariance(conn):
    """Mesma sequência de função em tons diferentes → similaridade 1.0."""
    a = fingerprint_from_db(conn, _id(conn, "iivi-em-do"))
    b = fingerprint_from_db(conn, _id(conn, "iivi-em-re"))
    assert similarity(a, b) == pytest.approx(1.0)


def test_distinct_song_is_less_similar(conn):
    """A música só-tônica/sub é menos parecida com o ii-V-I do que o par entre si."""
    do = fingerprint_from_db(conn, _id(conn, "iivi-em-do"))
    re = fingerprint_from_db(conn, _id(conn, "iivi-em-re"))
    other = fingerprint_from_db(conn, _id(conn, "so-tonica-sub"))
    assert similarity(do, re) > similarity(do, other)


def test_neighbors_top_k_no_self_ordered(conn):
    build_neighbors(conn, k=2)
    sid = _id(conn, "iivi-em-do")
    rows = conn.execute(
        "SELECT neighbor_id, rank, similarity FROM song_neighbor "
        "WHERE song_id = ? ORDER BY rank",
        [sid],
    ).fetchall()
    assert rows and len(rows) <= 2
    assert all(r[0] != sid for r in rows)  # sem auto-vizinho
    sims = [r[2] for r in rows]
    assert sims == sorted(sims, reverse=True)
    # o vizinho nº1 do ii-V-I em Dó é o ii-V-I em Ré (transposição idêntica)
    assert rows[0][0] == _id(conn, "iivi-em-re")


def test_neighbors_deterministic(conn):
    build_neighbors(conn, k=2)
    a = conn.execute("SELECT * FROM song_neighbor ORDER BY song_id, rank").fetchall()
    build_neighbors(conn, k=2)
    b = conn.execute("SELECT * FROM song_neighbor ORDER BY song_id, rank").fetchall()
    assert a == b


def test_neighbors_do_not_touch_gates(conn):
    def snap():
        return (
            conn.execute("SELECT COUNT(*) FROM v_gate_diminished").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM v_gate_d2").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM v_gate_cadence").fetchone()[0],
            conn.execute(
                "SELECT SUM(hash(song_id || COALESCE(function_code,''))) "
                "FROM chord_occurrence"
            ).fetchone()[0],
        )

    before = snap()
    build_neighbors(conn, k=2)
    assert snap() == before


def test_resolve_slug(conn):
    assert resolve_slug(conn, "iivi-em-do") is not None
    assert resolve_slug(conn, "musica-que-nao-existe") is None


def test_neighbors_up_to_date(conn):
    build_neighbors(conn, k=2)
    assert neighbors_up_to_date(conn) is True
