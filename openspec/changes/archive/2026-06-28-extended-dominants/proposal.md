## Why

Chediak (Vol. I, XXVIII, pp.107-108) define os **dominantes estendidos**: uma série de
dominantes em que cada um resolve **em outro dominante** por 4ªJ ascendente (5ªJ
descendente) — `C7M | A7 D7 | G7 | C7M`, onde `A7→D7→G7` é a cadeia. O ponto teórico é
explícito no livro: esses acordes **não levam número romano** porque "o som não está
diretamente vinculado à tonalidade"; marca-se só a **seta** de resolução, e a escala-acorde
é o **mixolídio**. O mesmo vale para os **SubV's estendidos** (cadeia separada por semitom
descendente, seta tracejada) e seus pares com II cadencial (**II V's** e **II SubV's
estendidos**).

Hoje o motor não conhece a cadeia: um `A7` que resolve em `D7` (ele próprio um dominante)
cai no ramo de **dominante secundário** e recebe `V7/II` — exatamente o número romano que
Chediak diz **não** existir nesse caso. A função fica presa à tonalidade quando deveria
pertencer à cadeia. É uma leitura de função (e de cifra analítica) infiel à fonte.

**Escopo (estreitado após sondagem ao vivo):** esta change cobre **XXVIII(a) — dominantes
estendidos por 4ªJ ascendente**, o caso definicionalmente inambíguo (ciclo de quintas). O
SubV estendido por **semitom** (XXVIII c/d) fica para change própria — a sondagem mostrou
que um par local de semitom (`F7→E7`) é indistinguível de um IV7→III7 de **blues** (Chediak
XXXIV), exigindo detecção de **cadeia** (≥2 elos cromáticos), não de par local, para não
regredir a leitura de blues. Ver `design.md` → Context.

- Detectar a **cadeia de dominantes estendidos**: um dominante cujo **próximo acorde
  também é um dominante** a 4ªJ acima (`interval(chord, next) == 5`) é um **dominante
  estendido** — pertence à cadeia, não a um grau diatônico.
- Introduzir o código de função `Dext` (Dominante Estendido) — escala-acorde **mixolídio**.
- **Suprimir o número romano aplicado** (`V7/x`) para o dominante estendido, fiel a
  Chediak ("não levam número romano"): a cifra analítica mostra o acorde + seta de
  resolução, não um grau atrelado à tonalidade. Só os acordes que **reconectam** à
  tonalidade no fim da cadeia (`V7/V`, `V7`, `I`) voltam a levar grau.
- Os **II V's estendidos** (XXVIII b) emergem por composição: o `iim7` que precede cada elo
  é o II cadencial já existente (`D2`); a novidade é só o elo dominante virar `Dext`.
  Documentado, sem ramo extra.

## Capabilities

### New Capabilities
<!-- Nenhuma: estende capabilities existentes. -->

### Modified Capabilities
- `harmonic-function`: a função harmônica passa a reconhecer o **dominante estendido**
  (`Dext`) — um dominante que resolve **em outro dominante** por **4ªJ ascendente** — em vez
  de o rotular `Dsec` (`V7/x`) atrelado à tonalidade. Escala-acorde mixolídio (Chediak
  XXVIII(a), pp.107-108).
- `roman-numeral-analysis`: um dominante estendido **não recebe** numeral aplicado
  (`V7/x`); a cifra analítica mostra o acorde + a seta de resolução, fiel a Chediak ("os
  dominantes estendidos não levam o número romano").
- `chord-scale-tensions`: o dominante estendido mapeia para **mixolídio** (Chediak XXVIII(a),
  p.339), com precedência sobre o default posicional (p.113) que mandaria um `II7`/`IV7`
  estendido para lídio b7; não sobrescreve a escala de dominante **alterado**.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/harmony.py` (novo ramo de
  dominante estendido **antes** da leitura `Dsec`), `constants.py` (entrada `Dext` em
  `HARMONIC_FUNCTIONS`), `roman.py` (suprimir `V7/x` quando o próximo acorde é um dominante
  a 4ªJ acima), `chord_scale.py` (param `next_chord` → mixolídio p/ estendido) +
  `analysis_service.py` (passa o próximo acorde ao `analyze_chord`). Testes em
  `test_applied_dominants.py`.
- **Limitação consciente:** o SubV estendido (semitom, seta tracejada — XXVIII c/d) fica
  **fora** desta change (colide com blues no par local; ver Context do design). Os pares II
  V estendidos não ganham marcação de "colchete de cadeia" (presentation); a função do
  `iim7` segue `D2`.
- **Não toca** `detect_key` → baseline **idêntico** (trava medida ao vivo, zero regressão
  das corretas). A trava real é a suíte: um `A7→D7` que era `Dsec V7/II` passa a `Dext`.
- **Dependência teórica:** estende o eixo das changes XVIII/XIX (alvo do dominante);
  fecha XXVIII(a). **Citação:** Chediak Vol. I, pp.107-108 (XXVIII), lida do livro (scan,
  offset 0). SubV estendido (XXVIII c/d) e acordes interpolados (XXIX) ficam para changes
  próprias.
