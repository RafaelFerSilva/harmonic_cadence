## Context

A extração canônica (`extract_chords_from_lines`) lê só linhas CHORD (`classify_line`, densidade
de `is_chord_token` via `fullmatch`) e extrai por `ChordPattern.find_all` (regex substring). Duas
perdas silenciosas: (1) token malformado (`D9/S`) tanka a densidade → linha vira LYRIC → some
inteira; (2) numa linha CHORD, `find_all` casa o prefixo (`D9`) e descarta o resto (`/S`) — chute
silencioso. O usuário escolheu **coleta visível** (diagnostics, sem travar) e escopo **alvo** (só
acorde malformado — prefixo válido + resto `/`/`(`).

Probe ao vivo (n=119): notações malformadas = `D9/S`×31, `C9/S`×15, `Db9/S`×8, `Eb9/S`×5,
`E9/S`×2, `Gm7(11)///Gb7(#11)///`×1. As 5 primeiras são baixo `/S` inválido; a última é DOIS
acordes colados por barra (não é malformado — resíduo vazio).

## Goals / Non-Goals

**Goals:**
- Notação malformada em posição de acorde → coletada em `diagnostics`, nunca silenciosa.
- Recuperar os acordes válidos das linhas que o malformado fazia sumir.
- Não chutar o prefixo do malformado (não emitir `D9` de `D9/S`).
- Zero regressão da extração de acordes válidos (n=119) + gates 119/119.

**Non-Goals:**
- Falha dura / exceção (escolha do usuário: coleta).
- Escopo estrito (qualquer não-acorde em linha CHORD).
- Interpretar `/S` (regra "nunca chute").

## Decisions

**D1 — `malformed_chord_token(token)` híbrido (prefixo + resíduo).** Malformado sse: `not
is_chord_token(token)` **e** `CHORD.match(token)` casa um prefixo não-vazio **e** o resto começa
com `/` ou `(` **e** o resíduo (o que sobra após `CHORD.sub(' ', token)` e remover a decoração
`/|%-` e espaços) é não-vazio. As duas últimas condições são complementares:
- O **escopo `/`/`(`** poupa palavra de letra (`Brasil` → resto `rasil`, não começa com `/`/`(`).
- O **resíduo** poupa acordes colados por barra (`Gm7(11)///Gb7(#11)///` → após remover os dois
  acordes e as barras, resíduo vazio → NÃO malformado; `find_all` extrai os dois).
*Alternativa rejeitada:* só-prefixo (sem resíduo) — marcaria o colado como malformado, perdendo 2
acordes válidos (regressão medida em `maria-ninguem`). Só-resíduo (sem escopo `/`/`(`) — marcaria
`Brasil` (resíduo `rasil`).

**D2 — Densidade conta o malformado como posição-de-acorde.** `classify_line`:
`hits = sum(is_chord_token(t) or malformed_chord_token(t) for t in tokens)`. Assim a linha
`D9/S / E/D / D9/S` volta a ser CHORD e os acordes válidos dela são recuperados. Risco de flipar
linha de letra é nulo (malformado exige prefixo-de-acorde + `/`/`(` glued, que letra não tem).

**D3 — Extração coleta o malformado, não o extrai.** `extract_chords_from_lines(..., unidentified:
list | None = None)`: itera por TOKEN nas linhas CHORD; token malformado → `unidentified.append` e
`continue` (não chuta o prefixo); senão → `find_all(token)` como hoje (barras/baixos/colados
intactos). Per-token `find_all` == per-linha `find_all` (acorde não cruza espaço) — **verificado
n=119: 0 regressão**. Backward-compat: sem `unidentified`, os malformados só não são extraídos (o
que já é o comportamento correto — não chutar).

**D4 — Coleta visível em `result["diagnostics"]`.** `_extract_chords` devolve `(chords,
unidentified)`; o call site agrega por token×contagem e injeta uma linha em `diagnostics` após
montar o `result` (ex.: `"Notação não identificada (ignorada, posição de acorde): D9/S ×31"`).
Reusa o canal `diagnostics` do `_safe_section` (mesma semântica de degradação visível).

## Risks / Trade-offs

- **[Músicas com `X9/S` ficam mais esparsas]** — os `X9` deixam de ser extraídos. → Mitigação:
  CORRETO por "nunca chute"; a linha que sumia inteira agora recupera os OUTROS acordes válidos
  (ganho líquido), e o furo fica **visível** no diagnostics. Se `/S` for uma notação real, o fonte
  se corrige (o diagnostics aponta onde).
- **[Falso-positivo de escopo]** — um token estranho tipo `C7(b13` (parêntese aberto) é marcado
  malformado. → Aceitável: é genuinamente não-identificável como está; reportar é honesto.
- **[Densidade flipar linha de letra]** — exige ≥60% de tokens malformados numa linha. → Nulo na
  prática (medido: só recupera acorde sensato, 0 regressão).

## Migration Plan

1. `cifra_core/lines.py`: `malformed_chord_token`; `classify_line` conta malformado; param
   `unidentified` em `extract_chords_from_lines` (iteração por token). Export no `__init__`.
2. `analysis_service._extract_chords` devolve `(chords, unidentified)`; call site agrega e injeta em
   `result["diagnostics"]`.
3. Testes unitários: `malformed_chord_token` (`D9/S`✓, `Am7/`✗, `A7(b9)/`✗, `B°/A/`✗,
   `Gm7(11)///Gb7(#11)///`✗, `Brasil`✗, `C7(b13`✓); classify recupera a linha `X9/S`; extração
   coleta e não chuta; diagnostics recebe a linha.
4. **Gate ao vivo:** baseline n=119 — os 4 gates **119/119**; extração de válidos sem regressão
   (só os `X9` chutados somem); `make test`/`make lint`.
