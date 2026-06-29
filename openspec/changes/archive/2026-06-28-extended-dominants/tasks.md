## 1. Trava (antes de tocar código)

- [x] 1.1 `make test` — **334 passed** (referência verde).
- [x] 1.2 Sondagem ao vivo (C maior): `A7 D7 G7 C` → `A7`=`Dsec V7/II`, `D7`=`Dsec V7/V`,
  `G7`=`D V7`, `C`=`T` (confirma o buraco do 4ªJ). `F7 E7 Eb7 D7` → `F7`=`SD IV7 blues`,
  `E7`=`T III7` — **colisão com blues** que estreitou o escopo (SubV estendido/semitom sai
  desta change). Ver `design.md` → Context.
- [x] 1.3 `scripts/key_baseline.py` — baseline de referência **86·74·81·97 / 18·19**
  (confirmado idêntico no quality gate, task 5.2). Não-toca-`detect_key` ⇒ idêntico.

## 2. Código de função `Dext` (constants.py + harmony.py)

- [x] 2.1 Adicionar `"Dext"` ao `FunctionCode` (harmony.py) e a entrada em
  `HARMONIC_FUNCTIONS` (constants.py): nome "Dominante Estendido", descrição citando
  Chediak XXVIII pp.107-108, escala-acorde mixolídio.
- [x] 2.2 Inserir, no bloco `if chord.is_dominant_seventh:` e **APÓS** o gate de blues 0a
  (logo antes de 0b/`Daux`/`Dsec`), o sub-ramo de cadeia: `next_chord and
  next_chord.is_dominant_seventh and _get_interval(chord.root, next.root) == 5` (4ªJ asc).
- [x] 2.3 Retornar `Dext` com nome "Dominante Estendido"; descrição cita Chediak XXVIII(a)
  pp.107-108.
- [x] 2.4 Escala-acorde **mixolídio** (escolha A): `next_chord` opcional em
  `recommended_scale`/`analyze_chord`; estendido força mixolídio sobre o default posicional
  (não sobre o alterado). `analysis_service` passa o próximo acorde via `enumerate`.

## 3. Supressão do numeral (roman.py)

- [x] 3.1 Em `roman_numeral`, antes de devolver `V7/{degree}`, se `next_chord` é dominante a
  **4ªJ acima** (`_get_interval(chord.root, next.root) == 5`) **e** o acorde não é I7/IV7
  blues (`pos not in (0, 5)`, espelhando o gate da função), devolver a **cifra simples** do
  acorde (sem `V7/x`).

## 4. Testes (test_applied_dominants.py)

- [x] 4.1 Dominante estendido: `A7 D7` (C maior) → `A7` = `Dext` (não `Dsec V7/II`).
- [x] 4.2 Cadeia: `A7 D7 G7 C` → `A7`,`D7` = `Dext`; `G7` (alvo tônica) = `D`.
- [x] 4.3 Escala-acorde: `Dext` → mixolídio (`D7` estendido, não lídio b7).
- [x] 4.4 Numeral suprimido: `A7→D7` → `A7` (não `V7/II`) em `roman_numeral`.
- [x] 4.5 Guards: `E7 Am` segue `Dsec V7/vi`; `F7 Bb7` (IV7 blues) segue `SD`, não `Dext`;
  `Bb7 Eb7` vira `Dext` (era `Daux`).

## 5. Quality gate + docs

- [x] 5.1 `make test` verde (**341 passed**, +7); `make lint` limpo.
- [x] 5.2 `scripts/key_baseline.py` ao vivo: **86·74·81·97 / 95% (18/19)** — **idêntico** ao
  baseline (não toca `detect_key`); zero regressão confirmada.
- [x] 5.3 `ROADMAP.md` e `AGENTS.md` atualizados (dominantes estendidos XXVIII(a), pp.107-108;
  frente XXVIII-a fechada, SubV estendido/XXIX/I7-funk abertas).
- [x] 5.4 `openspec validate extended-dominants --strict` passa; pronto para `openspec archive`.
