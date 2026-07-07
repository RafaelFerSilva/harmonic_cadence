-- persist-analysis-corpus — schema relacional que disseca o `result` do motor.
-- Grão = ocorrência de acorde. O banco guarda a VERDADE do motor (derivada,
-- regenerável), NUNCA a anotação da fonte (cc_key) nem gabarito de acurácia.
-- Dialeto portável (subconjunto SQLite/DuckDB); listas → JSON text (D7).

-- ── Proveniência ────────────────────────────────────────────────────────────
-- 1 materialização do corpus inteiro = 1 run (snapshot versionado, D3).
CREATE TABLE IF NOT EXISTS analysis_run (
    run_id          INTEGER PRIMARY KEY,
    engine_version  TEXT    NOT NULL,   -- versão do pacote harmonic_analysis
    git_sha         TEXT,               -- reprodutibilidade exata
    corpus_version  TEXT,               -- ex. "cifras/*.md n=170"
    generated_at    TIMESTAMP NOT NULL,
    n_songs         INTEGER NOT NULL
);

-- ── Dimensões (song-independent) ────────────────────────────────────────────
-- Os 14 function_code do motor (harmony.py) + label PT + is_repose + Chediak.
CREATE TABLE IF NOT EXISTS function_ref (
    function_code   TEXT PRIMARY KEY,
    label_pt        TEXT NOT NULL,
    macro_category  TEXT,               -- T | SD | D | other  (gates)
    is_repose       BOOLEAN NOT NULL,   -- False p/ D*/Sub* (coerência cadência)
    chediak_page    TEXT
);

-- As 7 famílias de cadência (cadence.py).
CREATE TABLE IF NOT EXISTS cadence_family_ref (
    family          TEXT PRIMARY KEY,
    is_resolving    BOOLEAN NOT NULL,   -- resolve na tônica?
    chediak_page    TEXT
);

-- Acorde parseado, ÚNICO no corpus. O parse é determinístico e independente de
-- música/versão do detector → dimensão global keyed por symbol (open question).
CREATE TABLE IF NOT EXISTS chord_vocab (
    symbol            TEXT PRIMARY KEY,
    root_pc           INTEGER NOT NULL, -- 0..11
    root_spelling     TEXT NOT NULL,    -- "Db" ≠ "C#" (ortografia Chediak)
    bass_pc           INTEGER,          -- inversão (NULL se raiz==baixo)
    bass_spelling     TEXT,
    quality           TEXT,             -- category().value (major/minor/dominant…)
    category          TEXT,             -- category().name  (DOMINANT/DIMINISHED…)
    third             TEXT,
    fifth             TEXT,
    seventh           TEXT,
    tensions          TEXT,             -- JSON list de semitons
    added             TEXT,             -- JSON list de semitons
    has_real_tritone  BOOLEAN NOT NULL  -- ≡ category == 'DOMINANT' (gate trítono)
);

-- ── Fato + cabeçalho ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS song (
    song_id         INTEGER PRIMARY KEY,
    run_id          INTEGER NOT NULL REFERENCES analysis_run(run_id),
    artist          TEXT,
    title           TEXT NOT NULL,
    slug            TEXT NOT NULL,
    source          TEXT NOT NULL,      -- 'local' | 'cifraclub'
    detected_key    TEXT,               -- detect_key → tônica soletrada
    detected_mode   TEXT,               -- major | minor
    center_pc       INTEGER,            -- chediak_functional_center → pitch-class
    center_mode     TEXT,
    center_status   TEXT NOT NULL,      -- 'agree' | 'diverge' | 'quarantine' (ledger)
    completeness    TEXT NOT NULL DEFAULT 'complete',
                                        -- 'complete' | 'suspect' | 'incomplete' —
                                        -- QUALIDADE DO DADO DE ENTRADA (ledger curado
                                        -- corpus/completeness.py), nunca defeito do motor
    n_chords        INTEGER NOT NULL,
    UNIQUE (run_id, slug)
);

-- A LINHA-FATO. Grão = um acorde numa posição (~8.500 linhas p/ n=170).
CREATE TABLE IF NOT EXISTS chord_occurrence (
    occ_id          INTEGER PRIMARY KEY,
    song_id         INTEGER NOT NULL REFERENCES song(song_id),
    position        INTEGER NOT NULL,   -- ordem na progressão (0-based)
    symbol          TEXT    NOT NULL REFERENCES chord_vocab(symbol),
    degree          TEXT,               -- "I", "V", "bII", "v" (min minúsc.)
    function_code   TEXT REFERENCES function_ref(function_code),
    strength        TEXT,               -- strong | medium | weak
    roman_numeral   TEXT,
    is_subv_chain   BOOLEAN DEFAULT FALSE, -- membro de cadeia SubV estendido
    is_ii_cadential BOOLEAN DEFAULT FALSE, -- ii cadencial (pré-passe)
    d2_resolved     BOOLEAN,            -- p/ D2: dominante resolve no alvo? (gate D4)
    UNIQUE (song_id, position)
);

-- ── Satélites (penduram no song_id / occ_id) ────────────────────────────────
-- Só acordes diatônicos têm escala (chord_scale.py devolve None p/ o resto).
CREATE TABLE IF NOT EXISTS chord_scale (
    occ_id    INTEGER PRIMARY KEY REFERENCES chord_occurrence(occ_id),
    scale     TEXT,                     -- "G mixolydian"
    tensions  TEXT,                     -- JSON list
    avoid     TEXT                      -- JSON list
);

-- Instância de cadência. Posição reconstruída na materialização (D5).
CREATE TABLE IF NOT EXISTS cadence (
    cadence_id    INTEGER PRIMARY KEY,
    song_id       INTEGER NOT NULL REFERENCES song(song_id),
    family        TEXT NOT NULL REFERENCES cadence_family_ref(family),
    from_position INTEGER,
    to_position   INTEGER,
    from_symbol   TEXT,
    to_symbol     TEXT,
    is_modulating BOOLEAN DEFAULT FALSE, -- deceptiva modulante?
    suppressed    BOOLEAN DEFAULT FALSE  -- reservado (o motor já suprime na saída)
);

CREATE TABLE IF NOT EXISTS tonal_region (
    region_id  INTEGER PRIMARY KEY,
    song_id    INTEGER NOT NULL REFERENCES song(song_id),
    start_pos  INTEGER,
    end_pos    INTEGER,
    region_key TEXT,
    score      REAL
);

CREATE TABLE IF NOT EXISTS modal_coloring (
    song_id   INTEGER PRIMARY KEY REFERENCES song(song_id),
    flavor    TEXT,                     -- mixolydian | phrygian
    evidence  TEXT,                     -- JSON list
    where_at  TEXT                      -- JSON list
);

CREATE TABLE IF NOT EXISTS diagnostic (
    diag_id  INTEGER PRIMARY KEY,
    song_id  INTEGER NOT NULL REFERENCES song(song_id),
    section  TEXT NOT NULL,             -- "chord_extraction", "voice_leading"…
    message  TEXT NOT NULL
);

-- Vereditos curados do ledger de trítono (anotação PRATA, derivada do corpus-em-código
-- `harmonic_analysis.corpus.tritone_adjudications`). Grão = ocorrência (song_id, position).
-- NÃO muta o coder: só anota o veredito+página Chediak p/ cruzar no ledger/report.
-- Regenerável no build; rollback = DROP + reverter a view do ledger.
CREATE TABLE IF NOT EXISTS tritone_adjudication (
    song_id   INTEGER NOT NULL REFERENCES song(song_id),
    position  INTEGER NOT NULL,
    symbol    TEXT NOT NULL,
    verdict   TEXT NOT NULL,            -- subv | chromatic_approach | emp_legitimate | dsec_deceptive | ambiguous
    chediak_page INTEGER,               -- NULL só p/ ambiguous (sem página, sem fato)
    note      TEXT NOT NULL,
    PRIMARY KEY (song_id, position)
);
