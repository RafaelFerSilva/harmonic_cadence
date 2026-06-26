## Why

A change `dominant-chord-scales` resolveu o dominante por **posição** (mixolídio /
lídio b7), mas deixou de fora os **dominantes alterados** (V7 com b9/#9/#5/b5/#11),
que pedem escalas próprias. Chediak (Vol. I, pp. 349-352, incl. o Quadro Geral
XII) tabela o mapa: alteração → escala.

Hoje um `G7(b9)` recebe mixolídio — mas a escala da fonte é a **diminuta
(semitom-tom)**; um `G7(#5)`, a **hexafônica**; um `G7(b5)`/`G7(#11)`, o **lídio
b7**; um `G7(#9)`, a **alterada**.

## What Changes

- `recommended_scale`: um dominante alterado mapeia para sua escala alterada pela
  alteração presente (lida do parse), com **precedência sobre a posição**:
  - `b5` ou `#11` → lídio b7
  - `#5` → hexafônica (tons inteiros)
  - `b9` → diminuta (semitom-tom)
  - `#9` (ou `b9`+`#9`) → alterada (super-lócrio)
- Novas escalas em `cifra_core`: `whole_tone`, `diminished` (semitom-tom),
  `altered`.

Fora de escopo: a distinção por **alvo** (V7b9 prep maior → diminuta vs prep menor
→ menor harmônica 5↓) — exige o acorde de resolução; o `b13` isolado segue
mixolídio (conservador). Escalas não-heptatônicas têm spelling aproximado (as
classes de altura ficam corretas, que é o que a análise de tensões usa).

## Capabilities

### Modified Capabilities
- `chord-scale-tensions`: dominantes alterados mapeiam para a escala alterada
  correspondente (diminuta/alterada/hexafônica/lídio b7).

## Impact

- `cifra_core/theory/scales.py`: `whole_tone`, `diminished`, `altered` em `MODE_PATTERNS`.
- `harmonic_analysis/domain/chord_scale.py`: `_altered_dominant_scale` + precedência.
- Testes: `G7(b9)`→diminuta, `G7(#9)`→alterada, `G7(#5)`→hexafônica, `G7(b5)`→lídio b7.
