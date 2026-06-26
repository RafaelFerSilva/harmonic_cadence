## Why

Chediak (Vol. I, p. 111) divide a cadência deceptiva em duas: **diatônica**
(V → grau diatônico) e **modulante** (V → acorde que leva a uma nova tonalidade).
Hoje a `harmonic-cadence` reporta tudo como uma "Deceptiva" única.

O projeto **já detecta modulação** (`segment_keys` → `tonal_regions`), mas essa
informação não chega à análise de cadência. Ligar as duas permite a distinção da
fonte: a deceptiva é modulante quando a resolução **cruza a fronteira de uma
região tonal** (mudança de tom).

## What Changes

- `analyze_cadences` aceita o tom de cada acorde (da região tonal) e divide a
  deceptiva em **"Deceptiva diatônica"** e **"Deceptiva modulante"**: modulante
  quando o V e seu alvo caem em regiões tonais de tons diferentes.
- `analysis_service` computa as regiões tonais **uma vez** e as fornece à cadência
  (além do relatório de modulação, que já as usava).
- Sem informação de região, a deceptiva cai em diatônica (padrão conservador).

Fora de escopo: cadência multi-tom (o V de uma região secundária analisado no tom
dela) — a análise de grau segue de tom único.

## Capabilities

### Modified Capabilities
- `harmonic-cadence`: a deceptiva passa a distinguir diatônica de modulante,
  usando a detecção de modulação.

## Impact

- `harmonic_analysis/domain/cadence.py`: `chord_keys` opcional; deceptiva dividida.
- `harmonic_analysis/services/analysis_service.py`: regiões tonais computadas uma
  vez e fornecidas à cadência.
- Testes: deceptiva diatônica (mesmo tom) vs modulante (tom muda).
