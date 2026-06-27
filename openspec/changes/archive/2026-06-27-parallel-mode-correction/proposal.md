## Why

A Fase B v1 (`tonal-center-detection`) resolveu a confusão **relativa** (maior ↔
relativa menor) por desempate cadencial. Mas o corpus n=60 expõe uma segunda
fraqueza igualmente frequente: a confusão **paralela** — mesma tônica, modo trocado
(Wave, Chega de Saudade, Valsinha detectadas em maior quando o tom é menor; Atrás da
Porta o inverso). Aqui o K-S erra **confiantemente** (a tônica está fora da banda de
empate), então o desempate da v1 não a alcança.

O sinal que distingue a paralela é diferente do da relativa: a **cadência não
desambigua** (a dominante é a mesma — `G7` é V de Dó maior *e* de Dó menor). O que
distingue maior de menor é a **qualidade dos acordes de tônica** (Chediak: a terça
da tônica define o modo). Uma correção de modo guiada por esse voto — e fechada pelo
**mesmo gate de âncora-baixo** da v1 — sobe o modo de 67% para 83% (n=60, simulado),
**sem regressão real**.

## What Changes

- Adicionar uma etapa de **correção de modo paralelo** ao `detect_key`, após a
  escolha do tom: se a tônica detectada é a **âncora tonal** (a música assenta nela —
  último baixo — ou há cadência autêntica para ela) **e** a qualidade dos acordes de
  tônica contradiz o modo do K-S com força (voto líquido ≥ 2), inverter o modo.
- O **gate da âncora-baixo** é o que torna a correção segura: ela só age na tônica em
  que a peça realmente repousa, nunca numa tônica impostora de confusão relativa
  (ex.: *Papel Marché*, detectada Lá menor mas que cadência em Dó — fica intocada).
- `detect_key` continua devolvendo `KeyEstimate` (mesma forma); a arbitragem
  modo↔tom e a segmentação a jusante seguem intactas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `key-detection`: a estimativa ganha uma **correção de modo paralelo** que, na
  tônica âncora, inverte o modo quando a qualidade dos acordes de tônica contradiz
  com força a leitura do K-S — atacando a confusão paralela (mesma tônica, maior ↔
  menor) que o desempate cadencial (relativa) não alcança.

## Impact

- **Código:** `domain/key_detection.py` (etapa de correção de modo + voto de
  qualidade de tônica, reusando o gate de âncora-baixo). Sem mudança de contrato.
- **Medição (n=60, simulado, indicativo):** modo 67%→83%, exata 50%→62%, relativa
  62%→72%. 7 músicas ERRO→exato; nenhuma resposta **correta** quebrada (uma lateral
  defensável: *Fotografia*, que de fato assenta na relativa).
- **Não regride** o gate sintético offline (`test_key_corpus`) nem a Sina (a tônica
  maior com acordes maiores não dispara o voto menor).
- **Fora de escopo (follow-ups):** segmentação das modulações reais como *regiões*
  (Wave/Chega assentam em maior no fim mas o CC rotula menor — aqui a correção
  acerta o gold, mas a leitura honesta é multi-região); tunar o EPS da banda.
