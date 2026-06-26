# Design — Localização PT-BR (camada de apresentação)

## Onde traduzir: na fronteira, não no modelo

O modelo interno fica em **inglês canônico** — `phrygian`, `minor`,
`lydian_dominant` são as chaves do código, dos `MODE_PATTERNS`, das specs. A
tradução acontece **só na apresentação** (relatórios + resumo do explainer). Não
toca algoritmo, é reversível e abre porta pra i18n real depois.

## O que traduz (e o que NÃO)

Traduz a **palavra**, mantém a **letra** do acorde (A–G é a cifra BR):

| Campo | EN | PT |
| --- | --- | --- |
| modo (tom) | major / minor | maior / menor |
| modo grego | ionian/dorian/phrygian/lydian/mixolydian/aeolian/locrian | jônico/dórico/frígio/lídio/mixolídio/eólio/lócrio |
| qualidade | dominant/diminished/half-diminished/augmented/suspended/power | dominante/diminuto/meio-diminuto/aumentado/suspenso/quinta |
| escala | `G mixolydian`, `G lydian_dominant`, `G whole_tone`, `G diminished`, `G altered` | `G mixolídio`, `G lídio b7`, `G hexafônica`, `G diminuta`, `G alterada` |

`D minor` → `D menor` (mantém o Ré como `D`); `G mixolydian` → `G mixolídio`.

Nota: **diminuto** (acorde) vs **diminuta** (escala) — mapas separados (gênero).

## Por que um módulo, não um `if` por site

Hoje já há um `'maior' if mode=='major'` solto no `formatter` — exatamente a
duplicação a evitar. Um `presentation/labels.py` com mapas + helpers
(`mode_pt`, `church_mode_pt`, `quality_pt`, `scale_pt`) centraliza, e os ~12
pontos de render passam a chamar o helper. Consolida o `MODE_NAMES_PT` legado.

## Não-objetivos

- Traduzir nomes de nota para Dó-Ré-Mi (a cifra BR usa A–G).
- i18n completo (catálogo de mensagens, múltiplos locales) — só PT-BR por ora.
- Traduzir chaves de dados usadas em lógica (ex.: `chord_qualities["major"]`).
