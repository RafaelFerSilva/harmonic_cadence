## Why

A detecção de tonalidade (`detect_key`) é Krumhansl-Schmuckler puro — correlação de
um histograma de pitch-classes contra 24 perfis. Esse histograma **descarta ordem e
função**, e é exatamente aí que mora a fraqueza sistemática: o K-S erra o **modo** em
~36% do corpus (n=28), por duas confusões que o conteúdo de notas não distingue —
**relativa** (maior ↔ relativa menor, perfis quase idênticos) e **paralela** (mesma
tônica, modo trocado).

A varredura dos casos reais mostrou que o sinal decisivo é o que o histograma joga
fora: **1º acorde, último acorde, e a cadência autêntica no fim** (V→I vs v→i). Ex.:
*Sampa* começa em `C` e termina `G7→C7M` (V→I de Dó maior), mas o K-S lê Lá menor —
sendo que **Dó maior é o próprio #1 alternativo do K-S**. Uma simulação (corpus n=28)
de um desempate cadencial conservador elevou modo 64%→71%, exata 46%→54%, relativa
61%→64% — e, crucialmente, **nenhuma música correta foi quebrada** (toda mudança caiu
sobre música já errada no baseline).

## What Changes

- Adicionar um estágio de **corroboração cadencial** ao `detect_key`, sobre o ranking
  K-S existente: uma pontuação por candidato `(tônica, modo)` a partir de sinais
  funcionais que o histograma ignora — 1º acorde = tônica; último acorde = tônica (com
  bônus se a qualidade casa o modo, penalidade se termina na tônica com o modo
  trocado); e **cadência autêntica** (acorde cujo baixo/fundamental é o dominante do
  candidato resolvendo na tônica) nos últimos acordes.
- **Desempate conservador:** re-rankear **apenas** candidatos cujo score K-S esteja
  dentro de uma banda de quase-empate (`EPS`) do topo. Fora da banda, o K-S prevalece
  — o estágio nunca sobrepõe um K-S confiante. `EPS` modesto e principiado, **não**
  maximizado in-sample.
- `detect_key` continua devolvendo `KeyEstimate` (mesma forma e campos). A arbitragem
  modo↔tom (`_mode_refines_key`) e a segmentação (`segment_keys`) ficam **intactas** a
  jusante.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `key-detection`: a estimativa K-S ganha um **estágio de corroboração cadencial** que
  desempata candidatos de score K-S quase-igual usando o centro tonal funcional (acorde
  final e cadência autêntica), reduzindo a confusão maior↔relativa-menor. A forma do
  resultado e o comportamento fora da banda de empate são preservados.

## Impact

- **Código:** `domain/key_detection.py` (estágio de corroboração + re-rank na banda).
  Sem mudança na forma de `KeyEstimate` nem nos consumidores a jusante.
- **Medição:** ganho **in-sample** (modo +~7pp, exata +~8pp) no n=28 — indicativo, não
  garantido; a validação real é a ampliação contínua do corpus. O gate sintético
  offline (`test_key_corpus`, 100%) **não** pode regredir.
- **Fora de escopo (follow-ups medidos):** override agressivo (para a paralela-erro
  tipo *Valsinha*); segmentação das modulações reais (*Wave*, *Chega de Saudade* —
  começam menor, terminam maior, rótulo único sempre erra → `segment_keys`); tônica de
  modos de igreja pelo K-S.
- **Risco:** baixo por construção (só age no quase-empate; não quebrou correto na
  simulação), mas o `EPS` é o ponto a não overfitar — tratado na disciplina de medição.
