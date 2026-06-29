## Why

Chediak (Vol. I, XXVIII c/d, pp.107-108) define os **SubV's estendidos**: uma série de
dominantes em que cada um resolve **em outro dominante por um semitom descendente**
(`C7M | F#7 | F7 | E7 | Eb7 | D7 | Db7 | C7M` — a seta tracejada do livro). É o espelho dos
dominantes estendidos por 4ªJ (`Dext`, já arquivado em `extended-dominants`), mas pela porta
do trítono/semitom. Como o dominante estendido, **não leva número romano** ("o som não está
diretamente vinculado à tonalidade") e tem escala-acorde **mixolídio** (p.339).

Esta frente foi **adiada** na change irmã por um motivo concreto: um par **local** de semitom
(`F7→E7`) é indistinguível de um `IV7→III7` de **blues** (Chediak XXXIV) e de dominantes de
passagem. A change irmã provou (sondagem ao vivo) que detectar por par local regrediria a
leitura de blues — viola a lei de zero-regressão. A solução é **detecção de cadeia**: só uma
*série* real de dominantes descendo por semitom caracteriza o SubV estendido.

Hoje a cadeia sai incoerente: na sondagem de `C F#7 F7 E7 Eb7 D7 Db7 C`, os acordes alternam
`SubV7/IV`, `SD blues`, `T`, `SubV7/II`, `SD`, `SubV` — em vez de "todos estendidos, exceto o
terminal `Db7`".

## What Changes

- **Detecção de cadeia (pré-passe):** um helper de domínio varre a progressão inteira e acha
  **runs maximais** de dominantes-7 consecutivos em que cada par desce por **semitom**, de
  comprimento **≥3 acordes** (≥2 movimentos). Só os membros desses runs são SubV estendidos.
- **Classificação:** um membro de cadeia que resolve ½t abaixo **em outro dominante** vira
  `Dext` (reusa o código do estendido, sabor "SubV Estendido" no nome). O **terminal** do run
  (resolve ½t num **não-dominante**, ex. `Db7→C`) **não** é estendido — segue SubV primário.
- **Sem número romano** para os membros de cadeia (cifra analítica = o próprio acorde) e
  **escala-acorde mixolídio**, consistente com `Dext` por 4ªJ.
- **Override do gate de blues:** um membro de cadeia confirmado (ex. `F7` dentro da série)
  deixa de ser lido como `IV7 blues` — a verificação de cadeia precede o gate de blues. O par
  **isolado** `F7 E7` (sem cadeia) **continua** `SD blues`.
- **II SubV's estendidos (XXVIII d)** emergem por composição: o `iim7` que precede cada elo é
  o II cadencial (`D2`) já existente; a novidade é só o elo virar `Dext`. Documentado.

## Capabilities

### New Capabilities
<!-- Nenhuma: estende capabilities existentes (as mesmas 3 da change irmã). -->

### Modified Capabilities
- `harmonic-function`: a função passa a reconhecer o **SubV estendido** — um dominante,
  membro de uma cadeia de semitons descendentes (≥3), que resolve ½t abaixo em outro
  dominante — como `Dext`, em vez das leituras incoerentes atuais (`SubV7/x`, `SD blues`, `T`).
- `roman-numeral-analysis`: um SubV estendido **não recebe** numeral aplicado; a cifra
  analítica é o próprio acorde (fiel a "não levam número romano").
- `chord-scale-tensions`: um SubV estendido mapeia para **mixolídio** (Chediak p.339), com
  precedência sobre o default posicional, sem sobrescrever o dominante alterado.

## Impact

- **Código afetado:** `domain/harmony.py` (helper de detecção de cadeia + ramo no topo do
  bloco de dominante, antes do gate de blues; novo param opcional em `analyze_function`),
  `domain/roman.py` e `domain/chord_scale.py` (param opcional de cadeia), e os **3 call
  sites** que computam o conjunto de membros uma vez e passam o flag:
  `services/analysis_service.py:186`, `domain/functional_hmm.py:280`,
  `presentation/formatter.py:79`. Testes em `test_applied_dominants.py`.
- **Uma fonte da lógica de cadeia:** o helper de domínio é o único lugar que decide
  membership; os call sites só o consomem (não reimplementam).
- **Não toca** `detect_key` → baseline **idêntico** (trava ao vivo: 86·74·81·97 / 18·19,
  zero regressão das corretas). A trava é a suíte + o baseline.
- **Citação:** Chediak Vol. I, pp.107-108 (XXVIII c/d), lida do livro (scan, offset 0).
  Acordes interpolados (XXIX) ficam para change própria.
