## Why

A emissão do HMM hoje é **constante**: a macro-função determinística recebe
`PRIMARY_MASS=0.70` e o resto se espalha nas alternativas — independentemente de
quão confiável é o rótulo. Mas Chediak (pág. 92) qualifica a função por **força**:
I/IV/V são fortes (âncoras), II/VII meio-fortes, III/VI fracos (substitutos
ambíguos). Essa força já é calculada (`harmonic-function`) e já viaja no
`harmonic_analysis` (campo `strength`) — só não é usada pelo modelo probabilístico.

## What Changes

- Ponderar a massa de emissão pela **força funcional** do grau: forte concentra
  mais massa no rótulo determinístico; fraca espalha mais nas alternativas; sem
  força diatônica mantém o padrão.
- A ponte (`build_functional_parse`) passa a `strength` ao HMM; o
  `parse_progression` deriva a força do grau.
- **Sem regressão:** um parse só a partir de códigos (sem força) continua
  idêntico ao modelo não-ponderado.

Fora de escopo: transições, estados, e a estrutura de Viterbi/forward-backward.

## Capabilities

### Modified Capabilities
- `probabilistic-functional-parsing`: emissão ponderada pela força funcional.

## Impact

- `harmonic_analysis/domain/functional_hmm.py`: `_emission`/`parse_codes` aceitam
  força; `build_functional_parse`/`parse_progression` a fornecem.
- Testes: força concentra/espalha; código-só inalterado; determinismo preservado.
