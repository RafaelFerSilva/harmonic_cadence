-- persist-analysis-corpus — views de GATE (executáveis), LEDGER e ANALYTICS.
-- Uma view de gate retorna exatamente as linhas em VIOLAÇÃO: vazia = gate verde.
-- Paridade travada por teste (D8) SÓ contra os caminhos que o baseline executa
-- (diminuto/D2/cadência). Trítono é LEDGER de curadoria, não gate (ver D9):
-- o gate de trítono do baseline é no-op e o invariante tem exceções documentadas
-- (I7 tônico de blues/funk, empréstimo modal) pendentes de adjudicação Chediak.

-- ── GATE EXECUTÁVEL 1 — diminuto nunca é Emp/SD/T/Modal (Chediak XXI-XXII p.90) ─
CREATE OR REPLACE VIEW v_gate_diminished AS
SELECT o.song_id, o.position, o.symbol, o.function_code
FROM chord_occurrence o
JOIN chord_vocab v ON o.symbol = v.symbol
WHERE v.category = 'DIMINISHED'
  AND (o.function_code IS NULL
       OR o.function_code NOT IN ('D', 'Dsec', 'Dim'));

-- ── GATE EXECUTÁVEL 2 — todo D2 resolve no alvo (Chediak XIX p.100) ──────────
-- Intervalar (i,i+1,i+2): re-derivado no motor e persistido em d2_resolved (D4).
CREATE OR REPLACE VIEW v_gate_d2 AS
SELECT o.song_id, o.position, o.symbol, o.function_code
FROM chord_occurrence o
WHERE o.function_code = 'D2'
  AND (o.d2_resolved IS NULL OR o.d2_resolved = FALSE);

-- ── GATE EXECUTÁVEL 3 — cadência resolutiva com alvo não-repouso (XXXII p.110) ─
-- O alvo (acorde em to_position) precisa FUNCIONAR como repouso. Se o motor
-- suprime corretamente, esta view nasce vazia (paridade com o baseline).
CREATE OR REPLACE VIEW v_gate_cadence AS
SELECT c.song_id, c.family, c.from_symbol, c.to_symbol, o.function_code
FROM cadence c
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
JOIN chord_vocab v ON o.symbol = v.symbol
WHERE v.has_real_tritone = TRUE
  AND (o.function_code IS NULL
       OR (UPPER(o.function_code) NOT LIKE '%D%'
           AND UPPER(o.function_code) NOT LIKE '%SUBV%'))
  AND NOT (o.function_code = 'T' AND o.degree IN ('I', 'i'));

-- ── ANALYTICS — ledger de corroboração de centro (contagem, não acurácia) ────
CREATE OR REPLACE VIEW v_center_ledger AS
SELECT center_status, COUNT(*) AS n
FROM song
GROUP BY center_status;

-- ── ANALYTICS — bigrama de função sobre o corpus inteiro ────────────────────
CREATE OR REPLACE VIEW v_function_bigram AS
SELECT a.function_code AS from_fn,
       b.function_code AS to_fn,
       COUNT(*) AS n
FROM chord_occurrence a
JOIN chord_occurrence b
  ON a.song_id = b.song_id AND b.position = a.position + 1
GROUP BY a.function_code, b.function_code
ORDER BY n DESC;
