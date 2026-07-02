"""persist-analysis-corpus — schema, materialização, views de gate e paridade.

Não depende de `cifras/*.md` (gitignored, ausente em CI): monta um mini-corpus
inline num diretório temporário. Valida grão (ocorrência de acorde), integridade
de FK, os gates EXECUTÁVEIS (nascem verdes) e a paridade com os caminhos que o
`songbook_baseline.py` de fato executa (ver design D8/D9)."""

import textwrap

import pytest

from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus

# Duas progressões tonais limpas (ii-V-I e um secundário) — sem trítono lido como
# não-dominante forçado; o objetivo é validar a mecânica, não a musicologia.
_FIXTURES = {
    "teste-um": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Dm7` `G7` `C7M` `A7`

        ```
        Dm7 G7 C7M A7
        Dm7 G7 C7M
        ```
        """
    ),
    "teste-dois": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Em7` `A7` `Dm7` `G7` `C7M`

        ```
        Em7 A7 Dm7 G7 C7M
        ```
        """
    ),
}


@pytest.fixture
def corpus_db(tmp_path):
    cifras = tmp_path / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(body, encoding="utf-8")
    conn = init_db(str(tmp_path / "corpus.duckdb"))
    summary = build_corpus(conn, str(cifras / "*.md"))
    assert not summary.get("error"), summary
    return conn, summary


def _count(conn, sql):
    return conn.execute(sql).fetchone()[0]


def test_schema_and_seeds_applied(corpus_db):
    conn, _ = corpus_db
    assert _count(conn, "SELECT COUNT(*) FROM function_ref") == 14
    assert _count(conn, "SELECT COUNT(*) FROM cadence_family_ref") == 7
    # is_repose deriva da regra do motor: D*/Sub* = tensão.
    assert _count(
        conn, "SELECT COUNT(*) FROM function_ref WHERE function_code='D' AND is_repose"
    ) == 0
    assert _count(
        conn, "SELECT COUNT(*) FROM function_ref WHERE function_code='T' AND is_repose"
    ) == 1


def test_grain_is_chord_occurrence(corpus_db):
    conn, summary = corpus_db
    assert summary["n_songs"] == 2
    # teste-um tem 4+3=7 acordes; teste-dois tem 5 → 12 ocorrências.
    assert _count(conn, "SELECT COUNT(*) FROM chord_occurrence") == 12
    # posição única por música.
    assert _count(
        conn,
        "SELECT COUNT(*) FROM (SELECT song_id, position, COUNT(*) c "
        "FROM chord_occurrence GROUP BY 1,2 HAVING c>1)",
    ) == 0


def test_provenance_run_recorded(corpus_db):
    conn, summary = corpus_db
    row = conn.execute(
        "SELECT engine_version, n_songs FROM analysis_run WHERE run_id=?",
        [summary["run_id"]],
    ).fetchone()
    assert row[0] and row[1] == 2


def test_foreign_key_integrity(corpus_db):
    conn, _ = corpus_db
    # nenhum function_code órfão
    assert _count(
        conn,
        "SELECT COUNT(*) FROM chord_occurrence o LEFT JOIN function_ref f "
        "ON o.function_code=f.function_code "
        "WHERE o.function_code IS NOT NULL AND f.function_code IS NULL",
    ) == 0
    # nenhum symbol órfão
    assert _count(
        conn,
        "SELECT COUNT(*) FROM chord_occurrence o LEFT JOIN chord_vocab v "
        "ON o.symbol=v.symbol WHERE v.symbol IS NULL",
    ) == 0


def test_no_source_key_column_in_song():
    """O banco não guarda anotação de tom da fonte como verdade (cc_key aposentado)."""
    from harmonic_analysis.persistence import db as db_mod

    # A tabela song não inclui tom-da-fonte como verdade (só o comentário de design
    # menciona 'cc_key' para explicar a ausência).
    schema = db_mod._SCHEMA.read_text(encoding="utf-8")
    song_block = schema.split("CREATE TABLE IF NOT EXISTS song (")[1].split(");")[0]
    assert "cc_key" not in song_block
    assert "detected_key" in song_block and "center_status" in song_block


def test_executable_gates_born_green(corpus_db):
    conn, _ = corpus_db
    for view in ("v_gate_diminished", "v_gate_d2", "v_gate_cadence"):
        assert _count(conn, f"SELECT COUNT(*) FROM {view}") == 0, view


def test_parity_with_baseline_executable_paths(corpus_db):
    """As views de gate executáveis casam com os invariantes que o baseline EXECUTA
    (diminuto casualmente verde; D2 e cadência de fato rodam). Trítono é ledger, não
    entra na paridade (baseline é no-op)."""
    conn, _ = corpus_db
    service_results = _run_baseline_invariants(conn)
    assert _count(conn, "SELECT COUNT(*) FROM v_gate_d2") == service_results["d2"]
    assert _count(conn, "SELECT COUNT(*) FROM v_gate_cadence") == service_results["cad"]
    assert _count(
        conn, "SELECT COUNT(*) FROM v_gate_diminished"
    ) == service_results["dim"]


def _run_baseline_invariants(conn) -> dict:
    """Re-roda os invariantes EXECUTÁVEIS do baseline sobre os mesmos acordes."""
    import importlib.util
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(
        "songbook_baseline", root / "scripts" / "songbook_baseline.py"
    )
    bl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bl)

    from harmonic_analysis.services.analysis_service import AnalysisService

    svc = AnalysisService()
    dim = d2 = cad = 0
    songs = conn.execute("SELECT song_id, title FROM song ORDER BY song_id").fetchall()
    for song_id, title in songs:
        chords = [
            r[0]
            for r in conn.execute(
                "SELECT symbol FROM chord_occurrence WHERE song_id=? ORDER BY position",
                [song_id],
            ).fetchall()
        ]
        result = svc.analyze_song_data_structured(
            {"artist": "", "name": title, "cifra": [" ".join(chords)]}
        )
        dim += len(bl._diminished_invariant(chords, result))
        d2 += len(bl._d2_resolution_invariant(chords, result))
        cad += len(bl._cadence_coherence_invariant(result))
    return {"dim": dim, "d2": d2, "cad": cad}


def test_tritone_ledger_is_informational(corpus_db):
    """O ledger de trítono existe e é consultável (worklist), não bloqueia."""
    conn, _ = corpus_db
    # A view existe e retorna colunas de curadoria (pode ser 0 no fixture limpo).
    conn.execute("SELECT song_id, position, symbol, function_code "
                 "FROM v_ledger_tritone_nondominant LIMIT 1").fetchall()
