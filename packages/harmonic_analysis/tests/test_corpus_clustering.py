"""Camada C — agrupamento hierárquico das músicas por perfil harmônico.

Fixture inline: materializa músicas, agrupa e valida a spec
`harmonic-corpus-clustering`:
- k famílias sobre M músicas, cada música em uma; determinismo; idênticas juntas;
- medoid é o centro da família;
- a materialização NÃO altera tabelas-base nem gates (descritivo);
- saída/traços descritivos.
"""

import textwrap

import pytest

from harmonic_analysis.overlay.clustering import build_clusters, cluster_traits
from harmonic_analysis.overlay.similarity import resolve_slug
from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus

# Dois pares "idênticos" (ii-V-I em dois tons cada) + uma outlier só-tônica/sub.
_FIXTURES = {
    "iivi-do": "```\nDm7 G7 C7M\nDm7 G7 C7M\n```\n",
    "iivi-re": "```\nEm7 A7 D7M\nEm7 A7 D7M\n```\n",
    "iivi-mib": "```\nFm7 Bb7 Eb7M\nFm7 Bb7 Eb7M\n```\n",
    "so-tonica": "```\nC7M F7M C7M F7M\n```\n",
    "so-tonica-2": "```\nG7M C7M G7M C7M\n```\n",
}


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("clustering")
    cifras = tmp / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(textwrap.dedent(body), encoding="utf-8")
    c = init_db(str(tmp / "c.duckdb"))
    summary = build_corpus(c, str(cifras / "*.md"))
    assert not summary.get("error")
    return c


def _clusters(conn):
    """dict cluster_id -> set(song_id) a partir da view."""
    rows = conn.execute(
        "SELECT cluster_id, song_id FROM v_song_cluster"
    ).fetchall()
    out: dict = {}
    for cid, sid in rows:
        out.setdefault(cid, set()).add(sid)
    return out


def test_every_song_in_exactly_one_family(conn):
    summary = build_clusters(conn, k=2)
    assert summary["k"] <= 2
    clusters = _clusters(conn)
    all_ids = [sid for members in clusters.values() for sid in members]
    assert len(all_ids) == len(set(all_ids)) == summary["n_songs"]


def test_determinism(conn):
    build_clusters(conn, k=2)
    a = conn.execute("SELECT * FROM song_cluster ORDER BY song_id").fetchall()
    build_clusters(conn, k=2)
    b = conn.execute("SELECT * FROM song_cluster ORDER BY song_id").fetchall()
    assert a == b


def test_identical_profiles_share_family(conn):
    """Os ii-V-I (mesmo perfil de função em tons diferentes) caem juntos."""
    build_clusters(conn, k=2)
    clusters = _clusters(conn)
    ii = {resolve_slug(conn, s) for s in ("iivi-do", "iivi-re", "iivi-mib")}
    # Todos os ii-V-I no MESMO cluster.
    assert any(ii.issubset(members) for members in clusters.values())


def test_medoid_is_one_per_family(conn):
    build_clusters(conn, k=2)
    rows = conn.execute(
        "SELECT cluster_id, COUNT(*) FILTER (WHERE is_medoid) "
        "FROM song_cluster GROUP BY cluster_id"
    ).fetchall()
    for _cid, n_medoids in rows:
        assert n_medoids == 1  # exatamente um protótipo por família


def test_clustering_does_not_touch_gates(conn):
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
    build_clusters(conn, k=3)
    assert snap() == before


def test_k_capped_at_song_count(conn):
    """k maior que o nº de músicas não estoura — cada música vira sua família."""
    summary = build_clusters(conn, k=999)
    assert summary["k"] == summary["n_songs"]


def test_cluster_traits_are_descriptive(conn):
    build_clusters(conn, k=2)
    clusters = _clusters(conn)
    some = list(next(iter(clusters.values())))
    traits = cluster_traits(conn, some)
    assert "functions" in traits and "cadences" in traits
    assert isinstance(traits["functions"], list)
