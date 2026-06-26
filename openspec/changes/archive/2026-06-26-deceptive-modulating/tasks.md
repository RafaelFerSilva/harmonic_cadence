# Tasks — deceptive-modulating

## 1. Cadência ciente de região
- [x] 1.1 `analyze_cadences(..., chord_keys=None)`: deceptiva dividida em
      "Deceptiva diatônica" e "Deceptiva modulante".
- [x] 1.2 Modulante quando `chord_keys[i] != chord_keys[i+1]`; senão diatônica.

## 2. Fornecer as regiões
- [x] 2.1 `analysis_service`: computar `segment_keys` uma vez, antes da cadência;
      `_chord_keys_for_regions` → tom por índice; passar à cadência.
- [x] 2.2 Reusar as mesmas regiões para `tonal_regions` do relatório.

## 3. Verificação
- [x] 3.1 Mesmo tom → "Deceptiva diatônica"; tom muda → "Deceptiva modulante".
- [x] 3.2 Sem `chord_keys` → diatônica (padrão).
- [x] 3.3 Suíte completa verde.
