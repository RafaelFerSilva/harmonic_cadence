-- persist-analysis-corpus — views de GATE (executáveis), LEDGER e ANALYTICS.
-- Uma view de gate retorna exatamente as linhas em VIOLAÇÃO: vazia = gate verde.
-- Paridade travada por teste (D8) SÓ contra os caminhos que o baseline executa
-- (diminuto/D2/cadência). Trítono é LEDGER de curadoria, não gate (ver D9):
-- o gate de trítono do baseline é no-op e o invariante tem exceções documentadas
-- (I7 tônico de blues/funk, empréstimo modal) pendentes de adjudicação Chediak.

-- Escopo padrão = RUN CORRENTE: o banco guarda snapshots (analysis_run) para
-- comparação A/B, mas gates/ledger/analytics respondem pelo estado ATUAL do
-- motor — sem o filtro, dois builds somam (ledger dobrado). Comparação entre
-- runs é consulta direta às tabelas, não às views.
CREATE OR REPLACE VIEW v_song_current AS
SELECT * FROM song
WHERE run_id = (SELECT MAX(run_id) FROM analysis_run);

-- ── GATE EXECUTÁVEL 1 — diminuto nunca é Emp/SD/T/Modal (Chediak XXI-XXII p.90) ─
CREATE OR REPLACE VIEW v_gate_diminished AS
SELECT o.song_id, o.position, o.symbol, o.function_code
FROM chord_occurrence o
JOIN v_song_current sc ON o.song_id = sc.song_id
JOIN chord_vocab v ON o.symbol = v.symbol
WHERE v.category = 'DIMINISHED'
  AND (o.function_code IS NULL
       OR o.function_code NOT IN ('D', 'Dsec', 'Dim'));

-- ── GATE EXECUTÁVEL 2 — todo D2 resolve no alvo (Chediak XIX p.100) ──────────
-- Intervalar (i,i+1,i+2): re-derivado no motor e persistido em d2_resolved (D4).
CREATE OR REPLACE VIEW v_gate_d2 AS
SELECT o.song_id, o.position, o.symbol, o.function_code
FROM chord_occurrence o
JOIN v_song_current sc ON o.song_id = sc.song_id
WHERE o.function_code = 'D2'
  AND (o.d2_resolved IS NULL OR o.d2_resolved = FALSE);

-- ── GATE EXECUTÁVEL 3 — cadência resolutiva com alvo não-repouso (XXXII p.110) ─
-- O alvo (acorde em to_position) precisa FUNCIONAR como repouso. Se o motor
-- suprime corretamente, esta view nasce vazia (paridade com o baseline).
CREATE OR REPLACE VIEW v_gate_cadence AS
SELECT c.song_id, c.family, c.from_symbol, c.to_symbol, o.function_code
FROM cadence c
JOIN v_song_current sc ON c.song_id = sc.song_id
JOIN cadence_family_ref f ON c.family = f.family
JOIN chord_occurrence o
  ON o.song_id = c.song_id AND o.position = c.to_position
JOIN function_ref fr ON o.function_code = fr.function_code
WHERE f.is_resolving = TRUE
  AND fr.is_repose = FALSE
  AND c.suppressed = FALSE;

-- ── LEDGER (NÃO gate) — trítono real lido como não-dominante (D9) ────────────
-- Semântica idêntica ao baseline: função-alvo NÃO contém 'D' nem 'SUBV'
-- (case-insensitive), APÓS isentar a classe limpa I7-como-tônica (função `T` no
-- grau da tônica `I`/`i` — blues/funk, `i7-funk-anchor`; ver fix-baseline-noop-
-- gates). Worklist de adjudicação, não placar; informativo em `corpus gates`.
CREATE OR REPLACE VIEW v_ledger_tritone_nondominant AS
SELECT o.song_id, o.position, o.symbol, o.function_code
FROM chord_occurrence o
JOIN v_song_current sc ON o.song_id = sc.song_id
JOIN chord_vocab v ON o.symbol = v.symbol
WHERE v.has_real_tritone = TRUE
  AND (o.function_code IS NULL
       OR (UPPER(o.function_code) NOT LIKE '%D%'
           AND UPPER(o.function_code) NOT LIKE '%SUBV%'))
  AND NOT (o.function_code = 'T' AND o.degree IN ('I', 'i'));

-- ── ANALYTICS — ledger de corroboração de centro (contagem, não acurácia) ────
CREATE OR REPLACE VIEW v_center_ledger AS
SELECT center_status, COUNT(*) AS n
FROM v_song_current
GROUP BY center_status;

-- ── ANALYTICS — bigrama de função sobre o corpus inteiro ────────────────────
CREATE OR REPLACE VIEW v_function_bigram AS
SELECT a.function_code AS from_fn,
       b.function_code AS to_fn,
       COUNT(*) AS n
FROM chord_occurrence a
JOIN v_song_current sc ON a.song_id = sc.song_id
JOIN chord_occurrence b
  ON a.song_id = b.song_id AND b.position = a.position + 1
GROUP BY a.function_code, b.function_code
ORDER BY n DESC;

-- ═══ corpus-analytics — views musicológicas DESCRITIVAS (nunca placar) ═══════

-- ── Distribuição das cadências por família (instâncias + músicas + Chediak) ──
CREATE OR REPLACE VIEW v_cadence_distribution AS
SELECT c.family,
       f.is_resolving,
       f.chediak_page,
       COUNT(*) AS instances,
       COUNT(DISTINCT c.song_id) AS songs
FROM cadence c
JOIN v_song_current sc ON c.song_id = sc.song_id
JOIN cadence_family_ref f ON c.family = f.family
GROUP BY c.family, f.is_resolving, f.chediak_page
ORDER BY instances DESC;

-- ── Trigrama de função — as "frases" funcionais do corpus (D2 do design) ────
CREATE OR REPLACE VIEW v_function_trigram AS
SELECT a.function_code AS fn1,
       b.function_code AS fn2,
       c.function_code AS fn3,
       COUNT(*) AS n
FROM chord_occurrence a
JOIN v_song_current sc ON a.song_id = sc.song_id
JOIN chord_occurrence b
  ON a.song_id = b.song_id AND b.position = a.position + 1
JOIN chord_occurrence c
  ON a.song_id = c.song_id AND c.position = a.position + 2
GROUP BY a.function_code, b.function_code, c.function_code
ORDER BY n DESC;

-- ── Vocabulário por modo — qualidades de acorde × modo detectado ────────────
CREATE OR REPLACE VIEW v_vocab_by_mode AS
SELECT s.detected_mode,
       v.quality,
       COUNT(*) AS n,
       COUNT(DISTINCT o.symbol) AS distinct_symbols
FROM chord_occurrence o
JOIN v_song_current s ON o.song_id = s.song_id
JOIN chord_vocab v ON o.symbol = v.symbol
GROUP BY s.detected_mode, v.quality
ORDER BY s.detected_mode, n DESC;

-- ── Densidade de dominantes secundários/substitutos por música (D4) ─────────
-- Fiel ao conceito: dominante NÃO-primário = Dsec/Daux/Dext/SubV/Sub2.
CREATE OR REPLACE VIEW v_secondary_density AS
SELECT s.song_id,
       s.title,
       s.n_chords,
       COUNT(o.occ_id) FILTER (
           WHERE o.function_code IN ('Dsec', 'Daux', 'Dext', 'SubV', 'Sub2')
       ) AS secondary_count,
       ROUND(
           100.0 * COUNT(o.occ_id) FILTER (
               WHERE o.function_code IN ('Dsec', 'Daux', 'Dext', 'SubV', 'Sub2')
           ) / NULLIF(s.n_chords, 0), 1
       ) AS secondary_pct
FROM v_song_current s
LEFT JOIN chord_occurrence o ON o.song_id = s.song_id
GROUP BY s.song_id, s.title, s.n_chords
ORDER BY secondary_pct DESC;

-- ── Ledger de trítono AGRUPADO por padrão (insumo de adjudicação, D3) ────────
-- Espelha `degree_base` do motor: acidente inicial opcional + numeral romano,
-- caixa-alta. Transforma as ocorrências soltas em padrões adjudicáveis
-- (função-alvo × grau-base × qualidade) com contagem, músicas e exemplos.
CREATE OR REPLACE VIEW v_tritone_ledger_patterns AS
SELECT COALESCE(l.function_code, '(vazio)') AS function_code,
       COALESCE(
           NULLIF(upper(regexp_extract(
               COALESCE(o.degree, ''), '(?i)^[b#]?(vii|vi|iv|v|iii|ii|i)', 1
           )), ''),
           '?'
       ) AS degree_base,
       v.quality,
       COUNT(*) AS n,
       COUNT(DISTINCT l.song_id) AS songs,
       MIN(l.symbol) AS example_symbol
FROM v_ledger_tritone_nondominant l
JOIN chord_occurrence o
  ON o.song_id = l.song_id AND o.position = l.position
JOIN chord_vocab v ON l.symbol = v.symbol
GROUP BY 1, 2, 3
ORDER BY n DESC;
