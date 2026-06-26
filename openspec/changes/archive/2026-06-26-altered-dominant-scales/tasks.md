# Tasks — altered-dominant-scales

## 1. Escalas
- [x] 1.1 `whole_tone`, `diminished`, `altered` em `MODE_PATTERNS` (cifra_core).
- [x] 1.2 Teste: classes de altura corretas (ex.: C altered = {0,1,3,4,6,8,10}).

## 2. Mapa alteração → escala
- [x] 2.1 `_altered_dominant_scale(chord)` lê fifth/tensões do parse.
- [x] 2.2 `recommended_scale`: alterada tem precedência sobre a posição.

## 3. Verificação
- [x] 3.1 `G7(b9)`→diminished, `G7(#9)`→altered, `G7(#5)`→whole_tone,
      `G7(b5)`/`G7(#11)`→lydian_dominant; `G7` puro inalterado (mixolydian).
- [x] 3.2 Dialeto ± (`G7(9-)`≡`G7(b9)`); diatônicos inalterados.
- [x] 3.3 Suíte completa verde.
