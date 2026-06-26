## Why

A análise harmônica de hoje é **casamento de strings sobre o símbolo do acorde**: não há representação das classes de altura (pitch classes), dos graus do acorde, nem da ortografia enarmônica. Esse é o teto de vidro que impede precisão e profundidade — e ele já produz erros concretos:

- `NOTE_REPLACEMENTS` colapsa todos os bemóis em sustenidos (`Db→C#`), **destruindo o spelling** (`bII` e `#I` viram a mesma nota), do que depende qualquer cifragem funcional.
- `guess_key` adivinha a tonalidade pelo primeiro acorde / razão de menores; tonalidade errada derruba **toda** a análise, e a peça é analisada numa única tonalidade (sem modulação).
- A detecção de **dominante secundário** e de **substituto de trítono (SubV)** usa intervalos invertidos (ver Impact), perdendo casos legítimos e marcando errados.

Esta mudança estabelece a **fundação teórica** (Camada 1) sobre a qual as melhorias musicais seguintes se apoiam.

## What Changes

- Introduzir um núcleo de teoria musical em `cifra_core` (`theory/`): `PitchClass`, `Note` com **ortografia preservada** (letra + acidente), `Interval`, realização de acorde (símbolo → conjunto de classes de altura + notas do acorde) e escalas/modos como dados de primeira classe.
- Preservar o **spelling enarmônico** ao longo da análise; deixar de colapsar bemóis em sustenidos. **BREAKING (interno):** `normalize_note`/`NOTE_REPLACEMENTS` deixam de ser a base do cálculo de grau/função.
- Substituir `guess_key` por **detecção de tonalidade Krumhansl-Schmuckler** sobre um perfil de classes de altura derivado dos acordes, com **segmentação por modulação** (janela deslizante) que divide a música em regiões tonais.
- Corrigir a análise de **dominantes aplicados**: detectar `V7/x` pela resolução de quinta justa descendente (raiz→alvo = 5 semitons) e `SubV` (bII7) por estar um semitom **acima** da tônica.
- Ligar o núcleo e a nova detecção de tonalidade ao `HarmonicAnalysis`; introduzir um pequeno **corpus de validação** com tonalidades anotadas para medir acurácia e travar regressões.

Fora de escopo (Camada 2+): modos como centro tonal de 1ª classe, cifragem romana com inversões, condução de vozes/linha de baixo, escala-acorde/tensões, reharmonização, parsing funcional probabilístico. Esta change entrega só a fundação e as correções de correção.

## Capabilities

### New Capabilities
- `music-theory-core`: núcleo de teoria em `cifra_core` — classes de altura, notas com ortografia preservada, intervalos, realização de acordes em conjuntos de classes de altura e escalas/modos como dados.
- `key-detection`: detecção de tonalidade por Krumhansl-Schmuckler a partir dos acordes, com segmentação de modulação em regiões tonais.
- `applied-dominant-analysis`: identificação correta de dominantes secundários (`V7/x` por quinta descendente) e do substituto de trítono (`SubV`/bII7 por meio-tom acima da tônica).

### Modified Capabilities
<!-- Nenhuma alteração de requisito em capacidades existentes (cifra-core, song-provider, monorepo-structure): o núcleo theory é ADITIVO ao pacote cifra_core. -->

## Impact

- **Código (`cifra_core`)**: novo subpacote `theory/` (`pitch.py`, `chord_realize.py`, `scales.py`); `Cifra`/filtro/regex existentes inalterados.
- **Código (`harmonic_analysis/domain`)**: `harmony.py` passa a usar o núcleo theory para grau/intervalo/spelling; `guess_key` substituída por `key_detection.py`; a lógica de `Dsec`/`SubV` em `analyze_function` é corrigida.
- **Correção de bugs (intervalos)**: `Dsec` hoje exige `_get_interval(chord.root, target)==7` (devia ser `5` — V7 resolve uma 5ª justa **abaixo**); `SubV` hoje exige `_get_interval(chord.root, key)==1` (devia ser `11` — bII7 está um semitom **acima** da tônica).
- **Spelling**: o colapso `Db→C#` (`NOTE_REPLACEMENTS`) deixa de governar a análise; a ortografia passa a depender do contexto de tonalidade.
- **Testes**: corpus de validação de tonalidade anotado + testes de unidade do núcleo e dos dominantes aplicados.
- **Sem impacto** em scraping, providers, cache, CLI ou empacotamento.
