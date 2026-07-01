# Tasks — report-unidentified-notations

> Notação malformada em posição de acorde → coleta VISÍVEL em `diagnostics` (não silenciosa, não
> chute). Detecção híbrida (prefixo válido + resto `/`/`(` + resíduo com lixo). Escopo:
> `cifra_core/lines.py` + `__init__` + `analysis_service.py` + testes.

## 1. Trava de baseline (referência)

- [x] 1.1 Probe n=119: registrar os tokens malformados (`D9/S`×31, `C9/S`×15, `Db9/S`×8, `Eb9/S`×5,
      `E9/S`×2, `Gm7(11)///Gb7(#11)///`×1) e provar **0 regressão real** (só os `X9` chutados somem).
      `songbook_baseline.py`: 4 gates **119/119** (referência a não regredir).

## 2. Detecção do acorde malformado

- [x] 2.1 `cifra_core/lines.py`: `malformed_chord_token(token) -> bool` — `not is_chord_token` +
      `CHORD.match` casa prefixo não-vazio + resto começa com `/`/`(` + resíduo (após `CHORD.sub`
      + remover `/|%-`/espaço) não-vazio. Export em `cifra_core/__init__.py`.

## 3. Densidade + extração

- [x] 3.1 `classify_line`: `hits` conta `is_chord_token(t) or malformed_chord_token(t)` (a linha
      malformada volta a ser CHORD).
- [x] 3.2 `extract_chords_from_lines`: novo param `unidentified: list | None = None`; iterar por
      TOKEN nas linhas CHORD; malformado → `unidentified.append` + `continue` (não chuta); senão
      `find_all(token)` como hoje (whitelist de raiz-nua preservada).

## 4. Coleta visível no motor

- [x] 4.1 `analysis_service._extract_chords` devolve `(chords, unidentified)`; call site (linha ~296)
      desempacota, agrega por token×contagem e injeta em `result["diagnostics"]` após `_build_result`.

## 5. Testes

- [x] 5.1 `malformed_chord_token`: `D9/S`✓, `C7(b13`✓; `Am7/`✗, `A7(b9)/`✗, `B°/A/`✗,
      `Bb7(9)///`✗, `Gm7(11)///Gb7(#11)///`✗, `Brasil`✗, `Em`✗.
- [x] 5.2 `classify_line`: linha `D9/S / E/D / D9/S` → CHORD (antes LYRIC).
- [x] 5.3 Extração: `unidentified` recebe o `D9/S`; o `D9` NÃO é extraído; `E/D` é.
- [x] 5.4 Motor: `analyze_song_data_structured` de uma cifra com `X9/S` → `result["diagnostics"]`
      cita a notação; a música é analisada (não trava).

## 6. Gate ao vivo + docs

- [x] 6.1 `songbook_baseline.py` n=119: 4 gates **119/119** (sem regressão); extração de válidos
      idêntica exceto os `X9` chutados (agora reportados). `make test` verde, `make lint` limpo.
- [x] 6.2 AGENTS: registrar a coleta visível de notação não-identificada.
      `openspec validate report-unidentified-notations --strict` passa.
