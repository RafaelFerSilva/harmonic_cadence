## Why

A detecção de tonalidade tinha o bug-fundação sinalizado na exploração inicial
(*"dois detectores votando sem árbitro"*): `detect_mode` **sobrescrevia**
incondicionalmente o `detect_key` (Krumhansl-Schmuckler). Resultado real: a Sina
(Djavan), claramente **Lá maior**, era reportada como **Ré menor**.

Duas falhas se somavam:
1. `detect_mode` pegava a tônica pela **raiz do último acorde**. A Sina termina
   em `D/A` (Ré sobre pedal de Lá) → pegava `D`, não o centro `A`.
2. A classificação de modo dispara "frígio" de **notas incidentais** (o `D#` de
   um `G#m7`, secundários etc.) num tom maior — e sobrescrevia o `detect_key`
   sem checagem.

Sintoma no corpus: Wave (Tom Jobim, Ré maior) → "D phrygian/minor"; Oceano,
Sozinho idem.

## What Changes

- **Centro tonal pelo baixo mais frequente** (o pedal/finalis), com bônus para o
  primeiro e o último acorde — não a raiz do último acorde.
- **Arbitragem**: um modo só **refina** a tonalidade do `detect_key` quando
  concorda com ela na **tônica** E na **qualidade** (maior/menor). Se discordar,
  é descartado (cromatismo tonal, não modalismo) e a leitura tonal prevalece —
  e o `mode_info` é anulado para que **todas** as seções a jusante fiquem
  coerentes.

Fora de escopo: detectar modalismo genuíno quando o `detect_key` erra a tônica
(ex.: pega o relativo maior de um modo menor) — limitação conhecida, registrada.

## Capabilities

### Modified Capabilities
- `modal-tonal-center`: o modo só refina (não inverte) a tonalidade do
  `detect_key`; o centro tonal vem do baixo predominante.

## Impact

- `harmonic_analysis/domain/modal.py`: `_central_pc` (baixo predominante)
  substitui `_final_tonic_pc` em `detect_mode`.
- `harmonic_analysis/services/analysis_service.py`: `_mode_refines_key`
  (arbitragem) gateia o override; `mode_info` anulado quando rejeitado.
- Resultado no corpus: Sina→A maior, Wave→D maior, Oceano→D maior; Papel Marché
  mantém o refinamento genuíno (A frígio, ambos concordam em Lá menor).
- Testes: regressão da Sina + unidade da arbitragem.
