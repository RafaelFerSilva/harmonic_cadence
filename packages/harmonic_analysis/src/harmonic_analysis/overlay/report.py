"""Relatório da worklist de anomalia funcional — Markdown PT-BR.

DESCRITIVO, nunca placar: todo número com denominador visível; a surpresa vem
acompanhada da contagem observada (por que é rara). O relatório declara em texto
que **o ML rankeia, o Chediak adjudica** — a worklist é candidata a olhar, não
veredito. Herda o guarda-corpo anti-placar do `corpus report` (testado).
"""

from __future__ import annotations

_DISCLAIMER = (
    "> Overlay estatístico **descritivo** (Camada C) — worklist de curadoria, nunca "
    "placar do modelo. O ML **rankeia**, o Chediak **adjudica**: cada linha é um caso "
    "a olhar página-a-página, **não** um defeito nem veredito. Surpresa alta = função "
    "rara no contexto (o denominador está à vista), o que pode ser MPB legítima e "
    "rica; a interseção com as worklists de trítono/centro é que prioriza a curadoria.\n"
)


def _table(headers: list[str], rows: list[tuple]) -> str:
    out = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for r in rows:
        out.append("| " + " | ".join("—" if v is None else str(v) for v in r) + " |")
    return "\n".join(out)


def render_anomaly_report(conn, top_n: int = 25) -> str:
    """Renderiza o relatório (string Markdown). Puro: só lê o banco."""
    parts: list[str] = []

    total = conn.execute("SELECT COUNT(*) FROM v_anomaly_worklist").fetchone()[0]
    n_songs = conn.execute(
        "SELECT COUNT(DISTINCT song_id) FROM v_anomaly_worklist"
    ).fetchone()[0]
    n_tritone = conn.execute(
        "SELECT COUNT(*) FROM v_anomaly_worklist WHERE in_tritone_ledger"
    ).fetchone()[0]
    n_center = conn.execute(
        "SELECT COUNT(*) FROM v_anomaly_worklist WHERE in_center_diverge"
    ).fetchone()[0]

    parts.append("# Worklist de anomalia funcional (Camada C)\n")
    parts.append(_DISCLAIMER)
    parts.append("## 1. Escopo\n")
    parts.append(
        f"- Ocorrências pontuadas: **{total}** em **{n_songs}** músicas (run corrente).\n"
        f"- Interseção com o ledger de trítono não-dominante: **{n_tritone}** de {total}.\n"
        f"- Ocorrências em músicas de centro `diverge`: **{n_center}** de {total}.\n"
    )

    # ── 2. Prioridade de adjudicação (surpresa × worklist de curadoria) ──────
    # Trilha B (ML) alimenta a Trilha A (Chediak): ranqueia por surpresa DENTRO de
    # cada worklist já suspeita por teoria. O trítono (o alvo mais afiado) é
    # mostrado inteiro, ordenado — não some sob a massa do centro divergente.
    parts.append(
        "\n## 2. Prioridade de adjudicação (surpresa × worklist existente)\n"
    )
    parts.append(
        "Onde a Trilha B (ML) alimenta a Trilha A (Chediak): a surpresa **ordena** o "
        "que adjudicar dentro das worklists que já são suspeitas por teoria.\n"
    )
    cols = ["Música", "Pos", "Acorde", "Função", "Grau",
            "Surpresa (bits)", "↳função", "↳grau"]
    select = (
        "SELECT title, position, symbol, function_code, degree, "
        "ROUND(surprise_bits, 2), ROUND(surprise_function, 2), "
        "ROUND(surprise_degree, 2) FROM v_anomaly_worklist"
    )

    tritone = conn.execute(
        f"{select} WHERE in_tritone_ledger ORDER BY surprise_bits DESC"
    ).fetchall()
    parts.append(
        f"\n### 2a. Ledger de trítono não-dominante — todas as {n_tritone}, "
        "ranqueadas\n"
    )
    parts.append(_table(cols, tritone))

    center = conn.execute(
        f"{select} WHERE in_center_diverge ORDER BY surprise_bits DESC LIMIT ?",
        [top_n],
    ).fetchall()
    parts.append(
        f"\n### 2b. Músicas de centro `diverge` — top {top_n} por surpresa "
        f"(de {n_center})\n"
    )
    parts.append(_table(cols, center))

    # ── 3. Mais surpreendentes no geral (contexto, não veredito) ─────────────
    top = conn.execute(
        f"{select} ORDER BY surprise_bits DESC LIMIT ?", [top_n]
    ).fetchall()
    parts.append(f"\n## 3. Mais surpreendentes no corpus (top {top_n})\n")
    parts.append(
        "Surpresa **bilateral** (média das direções) e **combinada** de dois canais — "
        "os componentes `↳função`/`↳grau` ficam à vista (muitas serão MPB legítima; "
        "grau `∅` = acorde sem grau diatônico):\n"
    )
    parts.append(_table(cols, top))
    parts.append("")
    return "\n".join(parts)


_ASSIST_DISCLAIMER = (
    "> Assistente de adjudicação por **precedente** (case-based reasoning, Camada C "
    "Fase 1). Cada linha é um veredito **DRAFT** — rascunhado por analogia a um caso já "
    "adjudicado por humano, **NUNCA** uma decisão. O símbolo/Chediak **adjudica**; o CBR "
    "**rascunha**. Citação é sempre **herdada** do precedente (fato já curado), nunca "
    "extraída do livro. A avaliação é **leave-one-out** vs. o veredito humano (hold-out "
    "do curador), não acurácia contra o coder. Precedente distante → draft `ambiguous` "
    "honesto.\n"
)


def _fmt_citation(cit) -> str:
    if cit is None:
        return "—"
    return f"Vol.{cit.volume} p.{cit.page}"


def render_precedent_report(conn, ledger: str = "tritone", k: int = 5) -> str:
    """Relatório MD PT-BR do assistente de precedente para um ledger.

    Mostra: a avaliação leave-one-out (taxa de confirmação humana, descritiva), os
    drafts das ocorrências PENDENTES (se houver), e os candidatos à armadilha ii-V.
    """
    from harmonic_analysis.overlay.precedent import (
        ii_v_trap_candidates,
        leave_one_out,
    )

    parts: list[str] = [
        f"# Assistente de adjudicação por precedente — ledger `{ledger}`\n",
        _ASSIST_DISCLAIMER,
    ]

    # ── Leave-one-out: o CBR reproduz o veredito humano quando ele é escondido? ──
    loo = leave_one_out(conn, ledger, k=k)
    parts.append(
        f"\n## Avaliação leave-one-out (k={loo['k']}) — descritiva, hold-out humano\n"
    )
    parts.append(
        f"O CBR reproduz **{loo['agree']}/{loo['n']}** dos vereditos humanos "
        f"({loo['rate']:.0%}) quando cada um é escondido da base. Mede o ALCANCE do "
        "precedente, não valida o corpus.\n"
    )
    rows = []
    for case, draft in loo["drafts"]:
        mark = "✓" if draft.verdict == case.verdict else "✗"
        rows.append((
            mark, case.slug,
            case.key[1] if len(case.key) > 1 else "—",
            case.verdict, draft.verdict,
            f"{draft.confidence:.0%} ({draft.denominator})",
            f"{draft.nearest_distance:.2f}",
        ))
    parts.append(_table(
        ["", "música", "pos", "humano", "draft (LOO)", "confiança", "dist"],
        rows,
    ))

    # ── Drafts das pendentes (sem veredito humano ainda) ────────────────────────
    pending = conn.execute(
        "SELECT slug, position, draft_verdict, chediak_page, confidence, "
        "denominator, nearest_slug, nearest_dist "
        "FROM v_draft_verdict WHERE ledger = ? ORDER BY confidence DESC, slug",
        [ledger],
    ).fetchall()
    parts.append(f"\n## Drafts pendentes (ocorrências sem veredito humano) — {len(pending)}\n")
    if pending:
        prows = [
            (slug, pos if pos is not None else "—", verdict,
             f"p.{page}" if page is not None else "—",
             f"{conf:.0%} ({denom})", near, f"{dist:.2f}")
            for slug, pos, verdict, page, conf, denom, near, dist in pending
        ]
        parts.append(_table(
            ["música", "pos", "draft", "pág (herdada)", "confiança", "precedente", "dist"],
            prows,
        ))
    else:
        parts.append(
            "_Nenhuma pendência: o ledger está 100% adjudicado por humano. O assistente "
            "entra em ação quando novas ocorrências suspeitas surgirem._\n"
        )

    # ── Candidatos à armadilha ii-V (ranking PRATA) ─────────────────────────────
    if ledger == "center":
        cands = ii_v_trap_candidates(conn)
        parts.append(f"\n## Candidatos à armadilha ii-V (PRATA) — {len(cands)}\n")
        parts.append(
            "> pós-Path D: detect pega o I (corrigido), funcional segue no ii do mesmo I. "
            "NÃO toca `detect_key` nem o placar de centro; candidatos a olhar, não veredito.\n"
        )
        crows = [
            (c["title"], c["slug"], "conhecido" if c["known"] else "**novo**")
            for c in cands
        ]
        parts.append(_table(["música", "slug", "status"], crows))

    return "\n".join(parts)
