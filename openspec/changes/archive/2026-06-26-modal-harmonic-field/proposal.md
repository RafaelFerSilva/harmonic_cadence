## Why

O campo harmônico modal (os acordes diatônicos de cada modo) hoje é **hardcoded**
em `constants.MODE_HARMONY` — e está **errado** em três modos quando conferido
contra Chediak (Vol. I, pp. 122-125):

- **frígio**: bVII deveria ser `m7` (bVIIm7), está `7`;
- **lídio**: #IV deveria ser `m7b5`, está `m7`; VI deveria ser `m7`, está `m7b5`;
- **mixolídio**: III deveria ser `m7b5` (IIIm7b5), está `m7`; VI deveria ser
  `m7`, está `m7b5`.

A causa-raiz é a mesma de sempre: dado teórico transcrito à mão em vez de
**derivado**. A correção robusta é derivar o campo da própria escala modal
(`build_scale`), correto por construção, e travá-lo contra as tabelas do Chediak.

## What Changes

- **`modal_field(tonic, mode)`**: deriva os 7 acordes diatônicos do modo
  (grau + qualidade) da escala — fonte única, correta por construção.
- **Nota característica por modo** (Chediak): dórico 6, frígio b2, lídio #4,
  mixolídio b7, eólio b6, lócrio b2/b6.
- **Corrigir** as entradas erradas de `MODE_HARMONY` (frígio/lídio/mixolídio).
- Cada campo travado por teste contra a tabela do Chediak.

Fora de escopo: acordes cadenciais/evitados por modo (documentados em Chediak,
ficam pra um próximo passo); modalismo puro vs misto; pentatônicas e sintéticos.

## Capabilities

### Modified Capabilities
- `modal-tonal-center`: expõe o campo harmônico modal derivado (Chediak-correto)
  e a nota característica de cada modo.

## Impact

- `harmonic_analysis/domain/modal.py`: `modal_field`, classificador de tétrade,
  `CHARACTERISTIC_NOTE`.
- `harmonic_analysis/domain/constants.py`: `MODE_HARMONY` frígio/lídio/mixolídio
  corrigidos.
- Testes: campo de cada modo == tabela Chediak; notas características.
