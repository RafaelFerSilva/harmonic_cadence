## Why

A fundação teórica (Camada 1: `music-theory-core`, `key-detection`, `applied-dominant-analysis`) deu altura, spelling e tonalidade corretos. Mas a análise ainda é rasa para o repertório-alvo:

- **Modos são cidadãos de segunda classe.** A detecção só faz maior/menor; um forró/baião em Mixolídio é lido como "maior com bVII emprestado", quando bVII–I é a *cadência* característica do modo. Música nordestina (mixolídia/lídia) fica mal descrita.
- **Não há cifragem romana de verdade.** Temos graus (I, ii, V7) mas sem **inversões** (I⁶, V⁶₄, V⁶₅) nem notação de acordes aplicados encadeados — o baixo (slash chord) é extraído e ignorado.
- **A condução de vozes é invisível.** Baixo descendente e *line clichés* — a alma de Jobim/Edu Lobo (ex.: *Insensatez* Dm Dm/C# Dm/C Dm/B) — não são detectados.
- **Sem análise de tensões.** No núcleo bossa/jazz/choro o valor está nas tensões (9, 11, 13, alterações) e nas escalas-acorde; o parser detecta 9/11/13 mas não os interpreta (disponíveis vs *avoid*).

Esta mudança entrega a **profundidade musical** (Camada 2), construída sobre a fundação da Camada 1.

## What Changes

- Introduzir **detecção de modo** (dórico, frígio, lídio, mixolídio, eólio, lócrio) como centro tonal de 1ª classe, com cadências e graus característicos; acordes diatônicos ao modo deixam de ser rotulados como "empréstimo".
- Introduzir **cifragem romana completa** (`roman-numeral-analysis`): numerais com qualidade, **inversões** a partir do baixo (figuras 6, ⁶₄, ⁶₅, ⁴₃, ⁴₂) e notação de acordes aplicados.
- Introduzir **análise de condução de vozes** (`voice-leading-analysis`): linha de baixo e seu movimento, pedais, baixo descendente diatônico/cromático e *line clichés*.
- Introduzir **escala-acorde e tensões** (`chord-scale-tensions`): mapear cada acorde (no contexto de tonalidade/modo) para escala(s) recomendada(s), tensões disponíveis e notas *avoid*.
- Expor as novas seções no resultado da análise e nos relatórios; estender o corpus de validação com exemplos modais e de inversão.

Fora de escopo (Camada 3): reharmonização, parsing funcional probabilístico (HMM/Viterbi), impressão digital de estilo por corpus, camada de explicação por LLM. Esta change é só profundidade analítica.

## Capabilities

### New Capabilities
- `modal-tonal-center`: detecção e análise em modo (igreja) como centro tonal, com cadências e graus característicos do modo.
- `roman-numeral-analysis`: cifragem romana com qualidade, inversões a partir do baixo e notação de acordes aplicados.
- `voice-leading-analysis`: linha de baixo, pedais, baixo descendente (diatônico/cromático) e *line clichés*.
- `chord-scale-tensions`: mapeamento escala-acorde, tensões disponíveis e notas *avoid* por acorde no contexto.

### Modified Capabilities
- `key-detection`: além de maior/menor, classificar o **modo** quando a coleção diatônica e o centro tonal indicarem um modo de igreja; estende (não remove) o comportamento atual.

## Impact

- **Código (`cifra_core/theory`)**: usa escalas/modos e realização já existentes; pode ganhar utilitários de inversão/figura de baixo e tabelas de escala-acorde.
- **Código (`harmonic_analysis/domain`)**: novos módulos `modal.py`, `roman.py`, `voice_leading.py`, `chord_scale.py`; `key_detection.py` ganha classificação de modo; `harmony.py`/`AnalysisService` passam a popular as novas seções (`modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`).
- **Baixo (slash chords)**: o `Chord.bass` já extraído passa a ser usado para inversões e linha de baixo.
- **Empréstimo modal**: a função `Emp` deixa de marcar acordes que são diatônicos a um modo detectado (passam a ser função modal).
- **Relatórios**: seções novas adicionadas; as existentes (cadências, progressões, function_stats) permanecem.
- **Testes**: suítes por capacidade + extensão do corpus (modal, inversões, baixo descendente, tensões).
- **Sem impacto** em scraping, providers, cache, CLI ou empacotamento.
