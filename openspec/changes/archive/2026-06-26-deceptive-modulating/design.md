# Design — Deceptiva modulante (Chediak p. 111 + detecção de modulação)

## A distinção da fonte

Chediak: a deceptiva é **diatônica** (V → grau diatônico do tom atual) ou
**modulante** (V → acorde que leva a nova tonalidade). O sinal decidível para
"leva a nova tonalidade" já existe: `segment_keys` segmenta a peça em **regiões
tonais**. A deceptiva é modulante quando o V e seu alvo pertencem a regiões de
**tons diferentes**.

## Plumbing

```
segment_keys(symbols) → regiões (start, end, key)
        │
        ▼  _chord_keys_for_regions → tom por índice de acorde
analyze_cadences(degrees, mode, symbols, chord_keys)
        │
        ▼  deceptiva (V → não-tônica):
           chord_keys[i] != chord_keys[i+1]  → "Deceptiva modulante"
           senão                              → "Deceptiva diatônica"
```

`analysis_service` já computava `segment_keys` para o relatório de modulação, mas
**depois** da cadência. A mudança o computa **uma vez, antes**, e reusa para os
dois (cadência + `tonal_regions`).

## Critério: região, não grau

Poderíamos usar um proxy de grau (alvo não-diatônico = modulante), mas ele
super-dispara: um V → acorde de empréstimo (um único acorde, sem mudança de tom)
viraria "modulante" indevidamente. A região tonal é mais fiel a "leva a uma nova
tonalidade" — um empréstimo isolado não forma região nova.

## Limitação registrada

A análise de grau é de **tom único** (o tom principal). Se o próprio V está numa
região secundária, seu grau pode não ser lido como "V" no tom principal e a
cadência não é detectada. Cadência multi-tom é um passo maior, fora desta change.
A janela de `segment_keys` (8 acordes) também não captura modulações curtas.

## Não-objetivos

- Reanalisar graus por região (cadência multi-tom).
- Calibrar a granularidade de `segment_keys`.
