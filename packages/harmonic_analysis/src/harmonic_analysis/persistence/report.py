"""Relatório musicológico de corpus (corpus-analytics) — Markdown PT-BR.

Consulta as views de analytics do banco e renderiza um relatório DESCRITIVO:
todo número com denominador visível, nenhuma métrica como acurácia/placar do
motor (o banco é view materializada da saída do motor, não ouro — a seção do
trítono é worklist de curadoria, não pass/fail).
"""

from __future__ import annotations

_MODE_PT = {"major": "maior", "minor": "menor", None: "—"}


def _rows(conn, sql: str) -> list[tuple]:
    return conn.execute(sql).fetchall()


def _one(conn, sql: str):
    return conn.execute(sql).fetchone()


def _table(headers: list[str], rows: list[tuple]) -> str:
    """Tabela Markdown simples."""
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join("—" if v is None else str(v) for v in r) + " |")
    return "\n".join(out)


def render_report(conn, top_n: int = 15) -> str:
    """Renderiza o relatório (string Markdown). Puro: só lê o banco."""
    parts: list[str] = []

    # ── 1. Corpus e proveniência ─────────────────────────────────────────────
    run = _one(
        conn,
        "SELECT run_id, engine_version, git_sha, corpus_version, generated_at "
        "FROM analysis_run ORDER BY run_id DESC LIMIT 1",
    )
    # Escopo = run corrente (o banco pode reter snapshots antigos p/ A/B).
    n_songs, n_occ = _one(
        conn,
        "SELECT (SELECT COUNT(*) FROM v_song_current), "
        "(SELECT COUNT(*) FROM chord_occurrence o "
        " JOIN v_song_current s ON o.song_id = s.song_id)",
    )
    ledger_center = _rows(
        conn, "SELECT center_status, n FROM v_center_ledger ORDER BY n DESC"
    )
    completeness = _rows(
        conn,
        "SELECT completeness, COUNT(*) FROM v_song_current "
        "GROUP BY completeness ORDER BY 2 DESC",
    )
    parts.append("# Relatório musicológico do corpus\n")
    parts.append(
        "> Estatística **descritiva** sobre a saída do motor (Chediak é o árbitro "
        "teórico). Nada aqui é placar do detector; o banco é derivado e "
        "regenerável.\n"
    )
    parts.append("## 1. Corpus e proveniência\n")
    parts.append(
        f"- Músicas: **{n_songs}** · ocorrências de acorde: **{n_occ}**\n"
        f"- Última materialização: run {run[0]}, motor {run[1]}"
        f"{f' ({run[2]})' if run[2] else ''}, corpus {run[3]}, em {run[4]}\n"
        f"- Corroboração de centro (ledger, não placar): "
        + ", ".join(f"{s}={n}" for s, n in ledger_center)
        + f" (sobre {n_songs} músicas)\n"
        f"- Completude do DADO DE ENTRADA (ledger curado, qualidade da fonte — "
        f"não defeito do motor): "
        + ", ".join(f"{s}={n}" for s, n in completeness)
        + "\n"
    )

    # ── 2. Cadências ─────────────────────────────────────────────────────────
    cad = _rows(
        conn,
        "SELECT family, chediak_page, instances, songs "
        "FROM v_cadence_distribution",
    )
    total_cad = sum(r[2] for r in cad)
    parts.append("## 2. Cadências (Chediak XXXII-XXXIII)\n")
    parts.append(f"Total de instâncias no corpus: **{total_cad}**.\n")
    parts.append(_table(
        ["Família", "Chediak", "Instâncias", f"Músicas (de {n_songs})"], cad
    ))

    # ── 3. Progressões funcionais ────────────────────────────────────────────
    bi = _rows(conn, f"SELECT from_fn, to_fn, n FROM v_function_bigram LIMIT {top_n}")
    tri = _rows(
        conn, f"SELECT fn1, fn2, fn3, n FROM v_function_trigram LIMIT {top_n}"
    )
    parts.append(f"\n## 3. Progressões funcionais (top {top_n})\n")
    parts.append("### Bigramas\n")
    parts.append(_table(["De", "Para", "n"], bi))
    parts.append("\n### Trigramas (as \"frases\" do corpus)\n")
    parts.append(_table(["1", "2", "3", "n"], tri))

    # ── 4. Vocabulário por modo ──────────────────────────────────────────────
    vocab = _rows(
        conn,
        "SELECT detected_mode, quality, n, distinct_symbols FROM v_vocab_by_mode",
    )
    vocab_pt = [(_MODE_PT.get(m, m), q, n, d) for m, q, n, d in vocab]
    parts.append("\n## 4. Vocabulário de qualidades por modo detectado\n")
    parts.append(_table(
        ["Modo", "Qualidade", f"Ocorrências (de {n_occ})", "Símbolos distintos"],
        vocab_pt,
    ))

    # ── 5. Dominantes secundários/substitutos ────────────────────────────────
    avg = _one(
        conn,
        "SELECT ROUND(AVG(secondary_pct), 1), SUM(secondary_count) "
        "FROM v_secondary_density",
    )
    top_sec = _rows(
        conn,
        "SELECT title, secondary_count, n_chords, secondary_pct "
        "FROM v_secondary_density WHERE secondary_count > 0 LIMIT 10",
    )
    parts.append("\n## 5. Dominantes secundários/substitutos (Dsec/Daux/Dext/SubV/Sub2)\n")
    parts.append(
        f"- Média do corpus: **{avg[0]}%** das ocorrências por música "
        f"(total {avg[1]} em {n_occ} ocorrências)\n"
        "- Músicas mais densas:\n"
    )
    parts.append(_table(["Música", "Secundários", "Acordes", "%"], top_sec))

    # ── 6. Worklist de curadoria — trítono não-dominante ─────────────────────
    total_ledger = _one(
        conn, "SELECT COUNT(*) FROM v_ledger_tritone_nondominant"
    )[0]
    patterns = _rows(
        conn,
        "SELECT function_code, degree_base, quality, n, songs, example_symbol "
        f"FROM v_tritone_ledger_patterns LIMIT {max(top_n, 10)}",
    )
    parts.append("\n## 6. Worklist de curadoria — trítono lido como não-dominante\n")
    parts.append(
        f"**{total_ledger} ocorrências** aguardam adjudicação Chediak (pós-isenção "
        "I7-tônica; ver `fix-baseline-noop-gates`). Agrupadas por padrão — cada linha "
        "é um caso teórico a adjudicar página-a-página, **não** um defeito contado:\n"
    )
    parts.append(_table(
        ["Função-alvo", "Grau", "Qualidade", "n", "Músicas", "Exemplo"], patterns
    ))

    # Distribuição por veredito adjudicado (anotação PRATA; foto de curadoria, não placar).
    verdicts = _rows(
        conn,
        "SELECT COALESCE(verdict, '(pendente)') AS v, COUNT(*) "
        "FROM v_ledger_tritone_nondominant GROUP BY 1 ORDER BY 2 DESC",
    )
    if verdicts:
        n_cited = _one(
            conn,
            "SELECT COUNT(*) FROM v_ledger_tritone_nondominant "
            "WHERE chediak_page IS NOT NULL",
        )[0]
        parts.append(
            f"\n**Adjudicação Chediak** (de {total_ledger}, "
            f"{n_cited} com página citada; `ambiguous` = resíduo honesto declarado):\n"
        )
        parts.append(_table(["Veredito", "Ocorrências"], verdicts))

    quarantined_ledger = _one(
        conn,
        "SELECT COUNT(*) FROM v_ledger_tritone_nondominant l "
        "JOIN v_song_current s ON l.song_id = s.song_id "
        "WHERE s.completeness != 'complete'",
    )[0]
    if quarantined_ledger:
        parts.append(
            f"\n> ⚠ {quarantined_ledger} das {total_ledger} ocorrências vêm de músicas "
            "com completude `suspect`/`incomplete` (cifra parcial) — pesar isso na "
            "adjudicação.\n"
        )
    parts.append("")

    return "\n".join(parts)
