"""fix-baseline-noop-gates — os gates executam de fato; trítono é ledger com isenção I7.

Testa a LÓGICA dos invariantes do `songbook_baseline.py` com `analysis` sintético
(determinístico, sem depender de `cifras/` nem do detector), e a isenção I7 na view
`v_ledger_tritone_nondominant`."""

import importlib.util
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def baseline():
    spec = importlib.util.spec_from_file_location(
        "songbook_baseline", _ROOT / "scripts" / "songbook_baseline.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _analysis(items):
    return {"harmonic_analysis": items}


def test_accessors_execute_not_noop(baseline):
    """A checagem roda de verdade: um diminuto lido como Emp é pego (antes: AttributeError
    engolido → nunca pegava nada)."""
    chords = ["Bb°", "C7M"]
    analysis = _analysis(
        [{"chord": "Bb°", "degree": "?", "function_code": "Emp"},
         {"chord": "C7M", "degree": "I", "function_code": "T"}]
    )
    assert baseline._diminished_invariant(chords, analysis) == ["Bb°→Emp"]


def test_diminished_gate_green_when_dominant(baseline):
    chords = ["Bb°"]
    analysis = _analysis([{"chord": "Bb°", "degree": "VII°", "function_code": "Dsec"}])
    assert baseline._diminished_invariant(chords, analysis) == []


def test_tritone_ledger_exempts_i7_tonic(baseline):
    """`I7` como tônica (função T, grau I) é isentado; dominante como T em grau não-tônica entra."""
    chords = ["A7", "G7"]
    analysis = _analysis(
        [{"chord": "A7", "degree": "I", "function_code": "T"},   # I7 tônico → isento
         {"chord": "G7", "degree": "VI", "function_code": "T"}]  # T-por-grau → ledger
    )
    assert baseline._tritone_nondominant_ledger(chords, analysis) == ["G7→T"]


def test_tritone_ledger_skips_dominant_family(baseline):
    chords = ["G7", "Db7"]
    analysis = _analysis(
        [{"chord": "G7", "degree": "V", "function_code": "D"},
         {"chord": "Db7", "degree": "bII", "function_code": "SubV"}]
    )
    assert baseline._tritone_nondominant_ledger(chords, analysis) == []


def test_d2_uses_properties_bass(baseline):
    """`_d2_resolution_invariant` usa `.properties.bass` (antes `tgt.bass` lançava)."""
    # Em7 A7 D7M : ii-V resolvendo por 4ªJ → D2 legítimo (sem defeito).
    chords = ["Em7", "A7", "D7M"]
    analysis = _analysis(
        [{"chord": "Em7", "degree": "ii", "function_code": "D2"},
         {"chord": "A7", "degree": "V", "function_code": "D"},
         {"chord": "D7M", "degree": "I", "function_code": "T"}]
    )
    assert baseline._d2_resolution_invariant(chords, analysis) == []


def test_view_exempts_i7_tonic(tmp_path):
    """A view v_ledger_tritone_nondominant aplica a mesma isenção I7 (grau I + função T)."""
    from harmonic_analysis.persistence.db import init_db

    conn = init_db(str(tmp_path / "c.duckdb"))
    conn.execute(
        "INSERT INTO analysis_run (run_id, engine_version, generated_at, n_songs) "
        "VALUES (1, 'test', now(), 1)"
    )
    conn.execute(
        "INSERT INTO song (song_id, run_id, title, slug, source, center_status, n_chords)"
        " VALUES (1, 1, 't', 't', 'local', 'agree', 2)"
    )
    conn.execute(
        "INSERT INTO chord_vocab (symbol, root_pc, root_spelling, quality, category, "
        "has_real_tritone) VALUES ('A7', 9, 'A', 'dominant', 'DOMINANT', TRUE)"
    )
    # duas ocorrências do MESMO acorde de trítono: uma T/grau I (isenta), uma T/grau VI (ledger)
    conn.execute(
        "INSERT INTO chord_occurrence (occ_id, song_id, position, symbol, degree, "
        "function_code) VALUES (1, 1, 0, 'A7', 'I', 'T'), (2, 1, 1, 'A7', 'VI', 'T')"
    )
    rows = conn.execute(
        "SELECT position, symbol FROM v_ledger_tritone_nondominant"
    ).fetchall()
    # só a ocorrência T/grau VI entra; a T/grau I (I7-tônica) é isentada.
    assert rows == [(1, "A7")]
