"""Materializador: motor → linhas do banco.

Roda o motor sobre o corpus local (`cifras/*.md` via `cifra_from_text`, sem rede) —
o MESMO caminho do `songbook_baseline.py`, para paridade — e disseca cada `result`
dict nas tabelas (grão = ocorrência de acorde). Degradação visível: música que
falha é registrada, não engolida.
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
from datetime import datetime

from cifra_core import cifra_from_text, extract_chords_from_lines
from cifra_core.slug import slugify
from cifra_core.theory import parse as parse_chord

from harmonic_analysis.corpus.completeness import completeness_for
from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis
from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.services.analysis_service import AnalysisService
from harmonic_analysis.validation import chediak_functional_center

# Extração idêntica ao baseline (bloco de código + whitelist do manifesto).
_CODE = re.compile(r"```(.*?)```", re.S)
_MANIFEST = re.compile(r"\*\*Acordes Utilizados:\*\*\s*(.+)")
_TICK = re.compile(r"`([^`]+)`")
_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _manifest(text: str) -> frozenset[str]:
    m = _MANIFEST.search(text)
    return frozenset(_TICK.findall(m.group(1))) if m else frozenset()


def _chords_from_md(path: str) -> list[str]:
    text = open(path, encoding="utf-8").read()
    blocks = _CODE.findall(text)
    body = "\n".join(blocks) if blocks else text
    cifra = cifra_from_text(body)
    return extract_chords_from_lines(cifra.cifra, known_chords=_manifest(text))


def _engine_version() -> str:
    try:
        from importlib.metadata import version

        return version("harmonic-analysis")
    except Exception:
        return "0.0.0"


def _git_sha() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
    except Exception:
        return None


def _vocab_row(symbol: str) -> dict:
    """Parse único de um acorde → linha de `chord_vocab` (fonte: cifra_core.theory)."""
    try:
        p = parse_chord(symbol)
        cat = p.category()
        return {
            "symbol": symbol,
            "root_pc": p.root.pitch_class,
            "root_spelling": str(p.root),
            "bass_pc": p.bass.pitch_class if p.bass is not None else None,
            "bass_spelling": str(p.bass) if p.bass is not None else None,
            "quality": cat.value,
            "category": cat.name,
            "third": p.third.value,
            "fifth": p.fifth.value,
            "seventh": p.seventh.value,
            "tensions": json.dumps(sorted(p.tensions)),
            "added": json.dumps(sorted(p.added)),
            "has_real_tritone": cat.name == "DOMINANT",
        }
    except Exception:
        m = re.match(r"^([A-G][#b]?)", symbol)
        return {
            "symbol": symbol,
            "root_pc": None,
            "root_spelling": m.group(1) if m else "",
            "bass_pc": None,
            "bass_spelling": None,
            "quality": "unknown",
            "category": "UNKNOWN",
            "third": None,
            "fifth": None,
            "seventh": None,
            "tensions": "[]",
            "added": "[]",
            "has_real_tritone": False,
        }


def _d2_resolves(chords: list[str], i: int) -> bool:
    """Re-deriva a resolução do D2 (Chediak XIX) — mesma lógica do baseline."""
    iv = HarmonicAnalysis._get_interval
    try:
        cur, dom, tgt = Chord(chords[i]), Chord(chords[i + 1]), Chord(chords[i + 2])
        return bool(
            cur.is_minor
            and dom.is_dominant_seventh
            and iv(cur.root, dom.root) == 5
            and (
                iv(dom.root, tgt.root) == 5
                or (
                    tgt.properties.bass is not None
                    and iv(dom.root, tgt.properties.bass) == 5
                )
            )
        )
    except Exception:
        return False


def _center_status(chords: list[str]) -> tuple[str, int | None, str | None]:
    """Ledger de corroboração: detect_key × chediak_functional_center."""
    est = detect_key(chords)
    det = (est.tonic_pc, est.mode) if est else None
    center = chediak_functional_center(chords)
    if center is None:
        return "quarantine", None, None
    status = "agree" if det == center else "diverge"
    return status, center[0], center[1]


def _find_cadence_positions(
    chords: list[str], parts: list[str], repose_at: set[int]
) -> tuple[int, int] | None:
    """Recupera (from_position, to_position) de um par de cadência `A → … → B`.

    Prefere uma ocorrência cujo ALVO funcione como repouso (paridade com o baseline,
    que dedup-a: a string só é defeito se TODAS as ocorrências são não-repouso)."""
    span = len(parts)
    candidates: list[int] = []
    for i in range(len(chords) - span + 1):
        if all(chords[i + k] == parts[k] for k in range(span)):
            candidates.append(i)
    if not candidates:
        return None
    for i in candidates:
        if (i + span - 1) in repose_at:
            return i, i + span - 1
    i = candidates[0]
    return i, i + span - 1


def build_corpus(conn, corpus_glob: str = "cifras/*.md") -> dict:
    """Materializa o corpus local no banco `conn`. Devolve um resumo."""
    paths = sorted(glob.glob(corpus_glob))
    if not paths:
        return {"error": f"Nenhuma cifra em {corpus_glob} (corpus local ausente)."}

    service = AnalysisService()

    # Coleta primeiro (para saber n_songs antes de gravar o run).
    songs: list[tuple[str, list[str], dict]] = []
    failures: list[str] = []
    for path in paths:
        name = os.path.basename(path)[:-3]
        chords = _chords_from_md(path)
        if not chords:
            continue
        result = service.analyze_song_data_structured(
            {"artist": "", "name": name, "cifra": [" ".join(chords)]}
        )
        if not result.get("success"):
            failures.append(f"{name}: {result.get('error')}")
            continue
        songs.append((name, chords, result))

    # ── analysis_run (snapshot versionado) ────────────────────────────────────
    run_id = (conn.execute("SELECT COALESCE(MAX(run_id), 0) + 1 FROM analysis_run")
              .fetchone()[0])
    conn.execute(
        "INSERT INTO analysis_run "
        "(run_id, engine_version, git_sha, corpus_version, generated_at, n_songs) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [run_id, _engine_version(), _git_sha(), f"{corpus_glob} n={len(songs)}",
         datetime.now(), len(songs)],
    )

    # Contadores de id (DuckDB sem auto-increment: geridos aqui).
    song_id = conn.execute("SELECT COALESCE(MAX(song_id), 0) FROM song").fetchone()[0]
    occ_id = conn.execute(
        "SELECT COALESCE(MAX(occ_id), 0) FROM chord_occurrence"
    ).fetchone()[0]
    cad_id = conn.execute(
        "SELECT COALESCE(MAX(cadence_id), 0) FROM cadence"
    ).fetchone()[0]
    reg_id = conn.execute(
        "SELECT COALESCE(MAX(region_id), 0) FROM tonal_region"
    ).fetchone()[0]
    diag_id = conn.execute(
        "SELECT COALESCE(MAX(diag_id), 0) FROM diagnostic"
    ).fetchone()[0]
    seen_vocab: set[str] = set()

    for name, chords, result in songs:
        song_id += 1
        status, c_pc, c_mode = _center_status(chords)
        slug = slugify(name)
        conn.execute(
            "INSERT INTO song (song_id, run_id, artist, title, slug, source, "
            "detected_key, detected_mode, center_pc, center_mode, center_status, "
            "completeness, n_chords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [song_id, run_id, "", name, slug, "local",
             result.get("key"), result.get("mode"), c_pc, c_mode, status,
             completeness_for(slug), len(chords)],
        )

        items = result.get("harmonic_analysis") or []
        romans = result.get("roman_numerals") or []
        chord_objs = [Chord(s) for s in chords]
        subv_members = HarmonicAnalysis.subv_extended_indices(chord_objs)
        ii_members = HarmonicAnalysis.ii_cadential_indices(chord_objs)

        # chord_vocab (upsert por symbol, global entre runs).
        occ_ids_by_pos: list[int] = []
        repose_at: set[int] = set()
        for i, sym in enumerate(chords):
            if sym not in seen_vocab:
                seen_vocab.add(sym)
                v = _vocab_row(sym)
                conn.execute(
                    "INSERT INTO chord_vocab (symbol, root_pc, root_spelling, bass_pc, "
                    "bass_spelling, quality, category, third, fifth, seventh, tensions, "
                    "added, has_real_tritone) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) "
                    "ON CONFLICT (symbol) DO NOTHING",
                    [v["symbol"], v["root_pc"], v["root_spelling"], v["bass_pc"],
                     v["bass_spelling"], v["quality"], v["category"], v["third"],
                     v["fifth"], v["seventh"], v["tensions"], v["added"],
                     v["has_real_tritone"]],
                )

            item = items[i] if i < len(items) else {}
            code = item.get("function_code")
            d2_resolved = _d2_resolves(chords, i) if code == "D2" else None
            if code and not (code.startswith("D") or code.startswith("Sub")):
                repose_at.add(i)

            occ_id += 1
            occ_ids_by_pos.append(occ_id)
            conn.execute(
                "INSERT INTO chord_occurrence (occ_id, song_id, position, symbol, "
                "degree, function_code, strength, roman_numeral, is_subv_chain, "
                "is_ii_cadential, d2_resolved) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                [occ_id, song_id, i, sym, item.get("degree"), code,
                 item.get("strength"), romans[i] if i < len(romans) else None,
                 i in subv_members, i in ii_members, d2_resolved],
            )

        # chord_scale (subsequência ordenada dos diatônicos → casa por symbol).
        p = 0
        for cs in result.get("chord_scales") or []:
            while p < len(chords) and chords[p] != cs.get("chord"):
                p += 1
            if p >= len(chords):
                break
            conn.execute(
                "INSERT INTO chord_scale (occ_id, scale, tensions, avoid) "
                "VALUES (?, ?, ?, ?)",
                [occ_ids_by_pos[p], cs.get("scale"),
                 json.dumps(cs.get("tensions") or []),
                 json.dumps(cs.get("avoid") or [])],
            )
            p += 1

        # cadence (reconstrói posição; D5).
        for family, pairs in (result.get("cadences") or {}).items():
            for pair in pairs:
                parts = [s.strip() for s in pair.split("→")]
                pos = _find_cadence_positions(chords, parts, repose_at)
                cad_id += 1
                conn.execute(
                    "INSERT INTO cadence (cadence_id, song_id, family, from_position, "
                    "to_position, from_symbol, to_symbol, is_modulating, suppressed) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    [cad_id, song_id, family,
                     pos[0] if pos else None, pos[1] if pos else None,
                     parts[0], parts[-1],
                     family == "Deceptiva modulante", False],
                )

        # tonal_region
        for r in result.get("tonal_regions") or []:
            reg_id += 1
            conn.execute(
                "INSERT INTO tonal_region (region_id, song_id, start_pos, end_pos, "
                "region_key, score) VALUES (?,?,?,?,?,?)",
                [reg_id, song_id, r.get("start"), r.get("end"), r.get("key"),
                 r.get("score")],
            )

        # modal_coloring (0..1)
        mc = result.get("modal_coloring")
        if mc:
            conn.execute(
                "INSERT INTO modal_coloring (song_id, flavor, evidence, where_at) "
                "VALUES (?, ?, ?, ?) ON CONFLICT (song_id) DO NOTHING",
                [song_id, mc.get("flavor"), json.dumps(mc.get("evidence") or []),
                 json.dumps(mc.get("where") or [])],
            )

        # diagnostic (degradação visível)
        for d in result.get("diagnostics") or []:
            diag_id += 1
            conn.execute(
                "INSERT INTO diagnostic (diag_id, song_id, section, message) "
                "VALUES (?, ?, ?, ?)",
                [diag_id, song_id, d.get("section"), d.get("error")],
            )

    return {
        "run_id": run_id,
        "n_songs": len(songs),
        "failures": failures,
    }
