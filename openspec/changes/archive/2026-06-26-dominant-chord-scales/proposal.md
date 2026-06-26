## Why

`recommended_scale` escolhe a escala-acorde só pela **posição da fundamental**,
ignorando a qualidade do acorde. Resultado: um acorde **dominante** numa
fundamental diatônica recebe a escala da tríade diatônica, não a escala
dominante. Ex.: `C7` (I7 blues, em Dó) cai em **C ionian** — mas C ionian tem
Si natural, e o C7 tem Sib. A escala certa é **C mixolídio** (ou blues).

Além disso, os dominantes de função especial que a `functional-analysis` já
classifica (`bVII7`, `IV7`, `II7`, `bVI7`) não têm escala — Chediak (Vol. I,
pág. 113) dá **lídio b7** para eles, e o livro inclusive nomeia essa escala como
o modo *nordestino* (pág. 121).

## What Changes

- **`recommended_scale` ciente da qualidade**: acorde dominante → escala
  dominante pela posição (Chediak p.113): `V7`/`I7` → mixolídio; `IV7`/`bVII7`/
  `II7`/`bVI7`/`VII7` → lídio b7. Não-dominante segue o mapeamento diatônico atual.
- **Nova escala `lydian_dominant`** (1 2 3 #4 5 6 b7) em `cifra_core` — o lídio b7
  / modo nordestino (Chediak pág. 121).

Fora de escopo: dominantes alterados → diminuta/alterada/hexafônica (V7b9, V7alt,
V7#5; Chediak P5·IV, pp. 342-346) — próximo passo; acordes cadenciais/evitados
por modo.

## Capabilities

### Modified Capabilities
- `chord-scale-tensions`: acordes dominantes mapeiam para uma escala dominante
  (mixolídio ou lídio b7), não para a escala da tríade diatônica.

## Impact

- `cifra_core/theory/scales.py`: `lydian_dominant` em `MODE_PATTERNS`.
- `harmonic_analysis/domain/chord_scale.py`: `recommended_scale` ciente da
  qualidade; mapa posição→escala dominante.
- Testes: `C7`→mixolídio; `Bb7`(bVII7)→lídio b7; diatônicos inalterados.
