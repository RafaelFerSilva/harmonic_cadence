## Why

O modelo de acorde é **bifurcado e baseado em strings**, e os dois motores erram
o mesmo input por mecanismos independentes:

- `harmonic_analysis.domain.chord.Chord._determine_quality` faz *sniffing* de
  substring (`"7" in s`, `"M" in symbol`) e chuta `MAJOR` no default.
- `cifra_core.theory.chord_realize._intervals_for` faz `contains()` sobre o
  sufixo e ignora a notação de cifra brasileira.

Evidência empírica no corpus (`data/`, 5 músicas, 886 acordes): **8 de 8** dos
acordes alterados mais comuns são realizados errados. O 2º acorde mais
frequente do projeto, `A7(13-)` (35 ocorrências), é realizado com 13ª natural
em vez de b13. Causas concretas:

- A notação **Cifra Club `grau±`** (`5-`=b5, `9+`=#9, `13-`=b13, `2-`=b9) é
  ~totalmente ignorada por `realize()`, que procura `#/b`. Toda tensão alterada
  da MPB real passa despercebida; `Em7(5-)` (meio-diminuto) vira Em7 com 5ª justa.
- `C7(#9)` conta a 9ª **e** a #9 (porque `"9"` mora dentro de `"#9"`).
- Acordes `sus` (`sus2`/`sus4`/`4`) e *power* (`5`) não são modelados.
- `°` nu vira tríade diminuta em vez de tétrade dim7.
- Extensão ímpar nua (`G9`, `G13`) não implica a 7ª.

A fonte de autoridade é **Almir Chediak, *Harmonia e Improvisação* Vol. I**
(`base_estudo/`), cuja sistemática de cifra o corpus segue. Esta change destila
os *fatos* das pp. 75–85 e 105 (não o texto/obras do livro) numa fonte de
verdade única para parsing de acorde.

## What Changes

- **Unificar o motor de acorde:** a realização passa a derivar de um **parse
  estruturado** (modelo de slots), de modo que a qualidade nomeada e o conjunto
  de classes de altura **nunca discordem**.
- **Corrigir `realize()`:** `sus`/power, `°`=dim7, dialeto `±`, `#9` sem
  duplicar a 9, extensão nua implicando a 7ª, e a nota do baixo entrando no
  conjunto realizado.
- **Aceitar os dois dialetos:** Chediak `#/b` (canônico, pág. 76) e Cifra Club
  `±` (variante do corpus), com equivalência de classe de grau (`4≡11`, `6≡13`,
  `2≡9`).
- **Estender a detecção** (`cifra-core`): capturar `±`, *power chords* e
  distinguir `/dígito` (tom acrescentado) de `/nota` (baixo invertido).
- **Faseamento (Opção 2):** fase 1 — o `Chord` do domínio passa a derivar tudo
  do motor de teoria (API pública estável, rede de testes intacta); fase 2 —
  extrair o `ParsedChord` para `cifra_core.theory` como fonte única.

Fora de escopo: *voicing*/dobramentos/supressões (a cifra não os estabelece —
Chediak pág. 78); classificação acorde-vs-letra (o falso-positivo `N.C.→C`, que
vive no portão de extração); OMR; e as 70 análises de músicas do livro (PARTE 4)
como dados ou *fixtures* (direitos de terceiros).

## Capabilities

### Modified Capabilities
- `music-theory-core`: realização de acordes corrigida; **novo** parse
  estruturado (`ParsedChord`/slots); **novo** suporte a dialetos de notação.
- `cifra-core`: padrão canônico de detecção estendido (`±`, power chords,
  desambiguação `/dígito` vs `/baixo`).

### New Capabilities
- (nenhuma — as mudanças são aditivas/correções sobre capacidades existentes.)

## Impact

- **`cifra_core.theory`**: novo parse estruturado em `chord_realize.py` (ou
  módulo `chord_parse.py`); `realize()` deriva dele; `ChordPattern` (`chords.py`)
  estendido.
- **`harmonic_analysis.domain.chord.Chord`**: internos delegam ao parse; API
  pública (`.symbol/.root/.quality/.is_minor/.is_dominant_seventh/.properties`)
  preservada na fase 1.
- **Consumidores** (`harmony`, `roman`, `chord_scale`, `voice_leading`,
  `reharmonization`, `functional_hmm`, `formatter`): inalterados na fase 1.
- **Testes**: a bateria do corpus (`A7(13-)`, `Em7(5-)`, `Db7(5+/9+)`, `G7M`,
  `D7(9/11+)`, `C6(9)`, `A7(4)`, `D#°`) entra como *fixture* de regressão.
- **Autoridade**: Chediak Vol. I, pp. 75–85 e 105, citado como racional no
  `design.md`; apenas fatos destilados, nas nossas palavras.
