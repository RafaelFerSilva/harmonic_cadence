## Context

Camada 1 entregou o núcleo `cifra_core/theory` (altura com spelling, intervalos, realização, escalas/modos como dados), detecção de tonalidade Krumhansl-Schmuckler com modulação, e dominantes aplicados corretos. O `Chord` já extrai o baixo (slash), e `HarmonicAnalysis` já computa graus/funções/cadências/progressões. O que falta é **profundidade musical**, especialmente para o repertório brasileiro (modos nordestinos; baixo descendente da bossa; tensões do choro/jazz).

## Goals / Non-Goals

**Goals:**
- Modo (igreja) como centro tonal de 1ª classe, com cadências e graus característicos.
- Cifragem romana completa com inversões a partir do baixo e acordes aplicados.
- Análise de condução de vozes: linha de baixo, pedais, baixo descendente, *line clichés*.
- Escala-acorde e tensões disponíveis / notas *avoid*.

**Non-Goals (Camada 3):** reharmonização, parsing funcional probabilístico (HMM/Viterbi), impressão digital de estilo por corpus, explicação por LLM.

## Decisions

### D1 — Modo por coleção diatônica + tônica, não por 24→84 perfis K-S
Detectar o modo a partir da **coleção de 7 classes de altura** dos acordes e do centro tonal (a tônica), classificando pelo padrão intervalar (já em `theory.MODE_PATTERNS`).
- **Por quê:** modos definem-se por *ausência* do trítono dominante/sensível e por graus característicos (bVII mixolídio, ♮6 dórica, bII frígia). Coleção+tônica é mais robusto e interpretável do que empilhar 84 perfis de correlação. Reusa o núcleo.
- **Alternativa:** 84 perfis K-S modais — rejeitado: perfis modais são fracos/ambíguos e pouco interpretáveis.

### D2 — RNA sobre o spelling do núcleo + baixo para inversão
Numeral = grau (via escala soletrada do `theory`) + qualidade (do `Chord`) + figura de inversão derivada da posição do **baixo** (`Chord.bass`) na pilha do acorde (fundamental/3ª/5ª/7ª → posição → figura). Aplicados reusam `applied-dominant-analysis`.
- **Por quê:** o spelling correto (Camada 1) é pré-requisito de RNA; o baixo já existe e é a fonte da inversão.
- **Alternativa:** inferir inversão por heurística sem baixo — rejeitado: o slash chord é a fonte canônica.

### D3 — Condução de vozes a partir da sequência de baixos
Extrair a linha de baixo (slash, senão fundamental) e analisar o movimento: pedais (baixo repetido sob acordes que mudam), baixo descendente (diatônico vs cromático por intervalos de −1/−2 consistentes) e *line clichés* (mesma fundamental com qualidade variando cromaticamente: m → m(maj7) → m7 → m6).
- **Por quê:** captura a marca de Jobim/Edu Lobo; tudo derivável do baixo + qualidade já disponíveis.

### D4 — Escala-acorde por tabela função→escala; tensões/avoid derivadas
Mapear (qualidade do acorde + função/grau) → escala-acorde padrão (Imaj7→Iônia, iim7→Dórica, V7→Mixolídia, iiø7→Lócria, …). Tensões disponíveis = notas da escala um tom acima de uma nota do acorde; *avoid* = nota da escala um semitom acima de uma nota do acorde (choca).
- **Por quê:** é a teoria escala-acorde padrão; determinístico e explicável. A regra "tom acima = tensão / semitom acima = avoid" gera o ♮11 avoid no Imaj7 automaticamente.
- **Alternativa:** escolher escala por conjunto de tensões presentes no símbolo — complementar, mas a função é o guia primário; alterações no símbolo refinam (V7alt→escala alterada) numa iteração futura.

### D5 — Camadas aditivas no resultado; relatório preservado
Novos módulos `modal.py`, `roman.py`, `voice_leading.py`, `chord_scale.py` em `harmonic_analysis/domain`; `AnalysisService` popula seções novas (`modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`). Seções existentes inalteradas.
- **Por quê:** evolução sem quebrar consumidores dos relatórios atuais.

### D6 — Modal vs funcional: o modo, quando ativo, governa
Quando um modo é detectado, graus/cadências/escala-acorde usam o contexto modal e a função `Emp` deixa de marcar o que é diatônico ao modo. Sem modo, tudo permanece tonal como hoje.

## Risks / Trade-offs

- **Modal vs tonal-com-empréstimo é ambíguo** → exigir evidência (ausência de sensível + presença do grau característico) e um limiar; validar no corpus; default conservador (tonal).
- **Inversão depende de baixo confiável** → `Chord.bass` existe; quando ausente, assume fundamental (sem figura).
- **Escala-acorde tem escolhas válidas concorrentes** (V7→Mixolídia vs alterada) → padrão por função + expor alternativas; refino por alterações do símbolo numa iteração futura.
- **Excesso de escopo (4 capacidades)** → cada módulo é independente e testável; entregar e validar um a um.
- **Ruído nos relatórios** → seções novas são opcionais e seccionadas; não poluem as existentes.

## Migration Plan

1. `key_detection`/`modal.py`: classificação de modo (coleção+tônica); expor o modo no `KeyEstimate`.
2. `roman.py`: numeral+qualidade+inversão (baixo) + aplicados; integrar a `HarmonicAnalysis`.
3. `voice_leading.py`: baixo, pedal, descendente, *line cliché*.
4. `chord_scale.py`: tabela escala-acorde + tensões/avoid.
5. `AnalysisService`: popular as seções novas; ajustar `Emp` para não marcar diatônicos do modo.
6. Estender o corpus de validação (modal, inversões, baixo descendente, tensões) + testes por capacidade.

## Open Questions

- Limiar de decisão modal vs tonal (quantas evidências do grau característico)?
- Representação dos numerais quando modal (numerais modais vs anotação relativa ao modo)?
- Escolha default de escala-acorde para o V7 (Mixolídia sempre, ou alterada quando há b9/#9/b13 no símbolo)?
- Agressividade da detecção de *line cliché* (quão estrito o "acorde estático")?
