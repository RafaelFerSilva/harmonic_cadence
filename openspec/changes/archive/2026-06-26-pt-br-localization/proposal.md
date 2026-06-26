## Why

A saída mistura português e inglês. As **funções** (`Tônica`, `Subdominante`) e
**cadências** (`Perfeita`, `Plagal`) já saem em PT, mas o **modo** sai cru em
inglês (`minor`, `phrygian`), as **qualidades** de acorde (`dominant`,
`diminished`) e os **nomes de escala** (`mixolydian`, `lydian_dominant`) idem.
Para o público BR — a ferramenta é pedagógica de MPB — isso é incoerência de
apresentação (a Sina aparecia como *"D minor"*; o esperado é *"D menor"*).

## What Changes

- **Módulo de rótulos PT-BR** na apresentação, traduzindo na fronteira: modo
  (maior/menor), modos gregos (frígio/mixolídio/dórico/lídio/eólio/lócrio/jônico),
  qualidades (dominante/diminuto/meio-diminuto/aumentado/suspenso) e escalas
  (mixolídio/lídio b7/hexafônica/diminuta/alterada).
- Aplicado em todos os relatórios (Markdown/HTML/JSON/CLI) e no resumo do
  explainer.
- A **letra do acorde permanece** (A–G — a convenção da cifra BR): traduz-se só a
  palavra (`D minor`→`D menor`, `G mixolydian`→`G mixolídio`).

**Decisão de design:** o modelo interno fica em **inglês canônico** (`phrygian`,
`minor`, `lydian_dominant` — chaves do código e dos `MODE_PATTERNS`); a tradução
é só de exibição. Padrão i18n: futuro-prova para outros idiomas, não toca
algoritmo.

## Capabilities

### Modified Capabilities
- `analysis-reporting`: os relatórios apresentam os termos harmônicos em
  português do Brasil.

## Impact

- `harmonic_analysis/presentation/labels.py` (novo): mapas + helpers PT.
- `presentation/reports/{markdown,html,json}.py`, `presentation/formatter.py`,
  `explain/prompt.py`: traduzem nos pontos de render.
- Consolida o `MODE_NAMES_PT` legado (parcial, chaves desalinhadas) num lugar só.
- Testes: render PT de modo, modo grego, qualidade e escala.
