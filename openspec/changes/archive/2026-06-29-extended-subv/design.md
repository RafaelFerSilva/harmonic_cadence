## Context

A change irmã `extended-dominants` (arquivada) implementou o **dominante estendido por 4ªJ**
(`Dext`): detecção **local** em `analyze_function` (próximo é dominante 4ªJ acima), supressão
do numeral em `roman.py`, mixolídio em `chord_scale.py`. O SubV estendido (XXVIII c/d) é o
espelho por **semitom descendente**, mas foi adiado porque um par local (`F7→E7`) é ambíguo
com blues `IV7→III7` (Chediak XXXIV) e dominantes de passagem — provado por sondagem.

A diferença arquitetural decisiva: o caso 4ªJ é seguro **localmente** (um dominante que sobe
4ªJ para outro dominante não tem leitura concorrente); o caso semitom **não** é — exige
distinguir uma *cadeia* real de um par isolado, o que precisa de contexto além dos vizinhos
imediatos. `analyze_function(chord, prev_chord, next_chord)` só vê prev/next (3 call sites),
insuficiente para os **extremos** de uma cadeia de 3+ acordes. Logo: **pré-passe** sobre a
sequência inteira.

Sondagem ao vivo (C maior): `C F#7 F7 E7 Eb7 D7 Db7 C` sai incoerente hoje (`SubV7/IV`, `SD
blues`, `T`, `SubV7/II`, `SD`, `SubV`). Desejado: F#7/F7/E7/Eb7/D7 = `Dext`, Db7 = `SubV`
(terminal). `F7 E7` isolado **continua** `SD blues`.

Não toca `detect_key` → baseline idêntico; a trava é a suíte + o baseline ao vivo.

## Goals / Non-Goals

**Goals:**
- Detectar **cadeias** de dominantes descendo por semitom (≥3 acordes) via pré-passe sobre a
  progressão inteira; classificar seus membros (exceto o terminal) como `Dext`.
- Suprimir o numeral e usar mixolídio para os membros, consistente com o `Dext` por 4ªJ.
- Override do gate de blues para membros confirmados; par isolado segue blues.
- Corrigir o gap `Dext → "X"` no `FUNCTION_MACRO` do HMM (deve ser `"D"`).

**Non-Goals:**
- Detecção por **par local** (a razão do adiamento) — só cadeia.
- Notação gráfica de seta tracejada / colchete tracejado dos II SubV's (apresentação).
- Ramo próprio para o `iim7` dos II SubV's estendidos (XXVIII d) — emerge por composição
  (`D2` + `Dext`), como nos II V's estendidos.
- Acordes interpolados (XXIX) — change futura.
- Tocar `detect_key`/`_tritone_gate`/parsing.

## Decisions

### D1 — Pré-passe `subv_extended_indices(chords, analysis) -> set[int]` (uma fonte)

Um helper de domínio em `harmony.py` varre a sequência e acha **runs maximais** onde cada par
consecutivo `(i, i+1)` satisfaz: ambos dominantes-7 **e** `_get_interval(chords[i].root,
chords[i+1].root) == 11` (semitom descendente, raiz cai ½t). Para cada run maximal de
comprimento **≥3 acordes** (≥2 movimentos), retorna `{j, …, k-1}` — **todos os membros menos
o último**. *Por quê excluir o último:* por maximalidade, o último acorde do run não resolve
½t num dominante (senão o run continuaria), então não é estendido — é o terminal (ex. `Db7→C`,
SubV primário). *Por quê ≥3 acordes:* um run de 2 (1 movimento, `F7→E7`) é o caso ambíguo
(blues/passagem) → retorna vazio → fica fora. É a desambiguação central do Chediak vs blues.

### D2 — Flag `subv_extended` em `analyze_function`, verificado ANTES do gate de blues

`analyze_function(chord, prev_chord, next_chord, subv_extended=False)`. No topo do bloco
`if chord.is_dominant_seventh:`, **antes** do gate de blues (0a), `if subv_extended: return
("Dext", "Dominante Estendido (SubV)", …)`. *Por quê antes de 0a:* um membro de cadeia que é
`IV7` (`F7`) deve sobrepor a leitura de blues; a confirmação de cadeia (pré-passe) é sinal mais
forte que a posição. Reusa o código `Dext` com o sabor "SubV" no nome (espelha a decisão de um
código só do `extended-dominants`).

### D3 — Threading do flag pelos call sites (consumo, não reimplementação)

Cada call site computa `members = subv_extended_indices(all_chords, analysis)` **uma vez** e
passa `i in members`:
- `services/analysis_service.py:186` (função) e o comprehension de `chord_scales` (escala).
- `services/analysis_service.py:424` e o wrapper `HarmonicAnalysis.roman_numeral` (roman).
- `domain/functional_hmm.py:280` e `presentation/formatter.py:79` (função).
`roman_numeral(chord, analysis, next_chord, subv_extended=False)` → quando `True`, devolve
`chord.symbol`. `recommended_scale(chord, analysis, next_chord=None, subv_extended=False)` →
quando `True`, mixolídio (mesma precedência do `Dext` 4ªJ: vence posicional, não o alterado).
*Por quê flag e não a sequência inteira nas funções:* mantém as assinaturas per-acorde simples
e a lógica de cadeia numa fonte só (o helper).

### D4 — Corrigir `FUNCTION_MACRO["Dext"] = "D"` no HMM

Hoje `Dext` não está no mapa → `FUNCTION_MACRO.get(code, "X")` devolve `"X"` (anômalo), tanto
para o estendido 4ªJ (já no `main`) quanto para o novo SubV. Um dominante estendido é
funcionalmente **dominante** → macro `"D"`. *Por quê aqui:* esta change toca o HMM (call site
280) e o bug afeta ambos os sabores de `Dext`; corrigir é fiel e retroativo.

## Risks / Trade-offs

- **[`F7` de blues vira `Dext` dentro de cadeia]** → é a leitura fiel (Chediak: cadeia
  cromática, não blues). O par isolado `F7 E7` (run de 2) **não** dispara — protegido pelo
  limiar ≥3. Trava: a suíte + baseline.
- **[Limiar ≥3 perde uma cadeia real de 2]** → escolha consciente: um run de 2 é
  indistinguível de blues sem mais contexto; preferir não-regressão. Documentado.
- **[Threading em muitos sites]** → mitigado por uma fonte única (o helper); os sites só
  consomem. Cada um computa o set uma vez (O(n)).
- **[Baseline]** → impossível regredir (`detect_key` intacto); rodo `scripts/key_baseline.py`.

## Migration Plan

1. Adicionar `subv_extended_indices` em `harmony.py` (com `_get_interval`/`is_dominant_seventh`).
2. Flag `subv_extended` em `analyze_function` (ramo no topo, antes do blues), `roman_numeral`,
   `recommended_scale`/`analyze_chord`.
3. Threading nos call sites (service ×3, formatter, functional_hmm), computando o set uma vez.
4. `FUNCTION_MACRO["Dext"] = "D"`.
5. Testes: cadeia `F#7 F7 E7 Eb7 D7 Db7 C` (membros = `Dext`, Db7 = SubV); par isolado
   `F7 E7` (SD blues); cadeia quebrada por não-dominante; roman suprimido; mixolídio; macro D.
6. `make test` + `make lint`; `scripts/key_baseline.py` (idêntico). ROADMAP/AGENTS.
7. Rollback = remover o helper, o flag e os usos; reverter o macro.

## Open Questions

- Uma cadeia que **não** termina na tônica nem reconecta (ex. termina num diatônico) — o
  último membro segue a regra "não resolve ½t em dominante → não estendido", caindo na leitura
  normal do alvo. Coberto pela exclusão do último no D1; refinável se a sondagem achar caso.
- Cadeias mistas (parte 4ªJ, parte semitom) — fora do escopo; cada porta dispara seu próprio
  ramo (`Dext` local 4ªJ ou flag de cadeia semitom). Sem conflito previsto.
