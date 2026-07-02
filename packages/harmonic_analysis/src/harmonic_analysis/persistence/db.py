"""Conexão DuckDB + aplicação de schema/views + seed das dimensões.

`is_repose` da `function_ref` é derivado programaticamente da MESMA regra do motor
(`cadence._non_repose`: código começa com `D`/`Sub` ⇒ tensão) — garante que a view
de coerência cadência×função case com o baseline sem drift manual.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # evita importar duckdb no import da CLI base
    import duckdb

_HERE = Path(__file__).parent
_SCHEMA = _HERE / "schema.sql"
_VIEWS = _HERE / "views.sql"

# Os 14 function_code do motor (harmony.py) → (label PT, macro-categoria, página Chediak).
# is_repose NÃO é hardcoded: deriva de _is_repose() abaixo (fonte única com o motor).
_FUNCTION_META: dict[str, tuple[str, str, str]] = {
    "T": ("Tônica", "T", "p.96"),
    "SD": ("Subdominante", "SD", "p.96"),
    "D": ("Dominante", "D", "p.96"),
    "D2": ("II cadencial", "D", "XIX p.100"),
    "SubV": ("SubV (dominante substituto)", "D", "XXVIII"),
    "Sub2": ("SubV secundário", "D", "XXVIII"),
    "Dsec": ("Dominante secundário", "D", "XVIII"),
    "Daux": ("Dominante auxiliar", "D", "XVIII p.99"),
    "Dext": ("Dominante estendido", "D", "XXVIII pp.107-108"),
    "Emp": ("Empréstimo modal", "other", "—"),
    "Modal": ("Acorde modal", "other", "—"),
    "Dim": ("Diminuto auxiliar", "D", "XXI-XXII p.90"),
    "Crom": ("Cromático", "other", "—"),
    "Outro": ("Outro/inválido", "other", "—"),
}

# 7 famílias de cadência (cadence.py) → (resolve na tônica?, página Chediak).
_CADENCE_META: dict[str, tuple[bool, str]] = {
    "Perfeita": (True, "XXXII p.110"),
    "Autêntica": (True, "XXXII p.110"),
    "Imperfeita": (True, "XXXII p.110"),
    "Plagal": (True, "XXXII p.110"),
    "Meia-cadência": (False, "XXXII p.110"),
    "Deceptiva diatônica": (False, "XXXIII p.111"),
    "Deceptiva modulante": (False, "XXXIII p.111"),
}


def _is_repose(code: str) -> bool:
    """Espelha `cadence._non_repose`: tensão = começa com `D` ou `Sub`."""
    return not (code.startswith("D") or code.startswith("Sub"))


def connect(path: str = "corpus.duckdb"):
    """Abre (ou cria) o banco DuckDB. Import tardio de `duckdb`."""
    import duckdb

    return duckdb.connect(path)


def _exec_script(conn: "duckdb.DuckDBPyConnection", sql: str) -> None:
    """Executa um script multi-statement (DuckDB aceita `;`-separado num execute)."""
    conn.execute(sql)


def seed_dimensions(conn: "duckdb.DuckDBPyConnection") -> None:
    """Popula `function_ref` e `cadence_family_ref` (idempotente)."""
    for code, (label, macro, page) in _FUNCTION_META.items():
        conn.execute(
            "INSERT INTO function_ref "
            "(function_code, label_pt, macro_category, is_repose, chediak_page) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (function_code) DO NOTHING",
            [code, label, macro, _is_repose(code), page],
        )
    for family, (resolving, page) in _CADENCE_META.items():
        conn.execute(
            "INSERT INTO cadence_family_ref (family, is_resolving, chediak_page) "
            "VALUES (?, ?, ?) ON CONFLICT (family) DO NOTHING",
            [family, resolving, page],
        )


def init_db(path: str = "corpus.duckdb"):
    """Cria o banco: aplica schema + views + seed. Devolve a conexão aberta."""
    conn = connect(path)
    _exec_script(conn, _SCHEMA.read_text(encoding="utf-8"))
    _exec_script(conn, _VIEWS.read_text(encoding="utf-8"))
    seed_dimensions(conn)
    return conn
