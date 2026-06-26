# Tasks — chord-parsing

## 1. Rede de regressão (antes de tocar no código)
- [x] 1.1 Extrair a bateria do corpus (`data/*.json`) como *fixture* de acordes
      reais: `A7(13-)`, `Em7(5-)`, `Db7(5+/9+)`, `G7M`, `C7M(5+)`, `D7(9/11+)`,
      `C6(9)`, `A7(4)`, `B2`, `D#°`, `G7(9/13)`.
- [x] 1.2 Anotar para cada um o conjunto de classes de altura esperado (verdade
      de teoria, conforme Chediak) — vira o oráculo dos testes de realização.

## 2. Dialetos e tokenização (parser)
- [x] 2.1 Tokenizador de sufixo de acorde que consome `#9`/`9+`, `b5`/`5-`,
      `b13`/`13-`, `2-`, `(...)` — sem `contains()`.
- [x] 2.2 Normalização de dialeto (`±` → `#/b`) e de classe de grau
      (`4≡11`, `6≡13`, `2≡9`).
- [x] 2.3 Testes: `C7(9-)`≡`C7(b9)`, `A7(2-/13-)`≡`A7(b9/b13)`, `C7(#9)` sem 9 natural.

## 3. Modelo de slots (`ParsedChord`)
- [x] 3.1 Definir `ParsedChord` (root, bass, third, fifth, seventh, added, tensions).
- [x] 3.2 Regra `seventh × tensions` (fase 1/2 do design): `°`→dim7, `6` bloqueia
      7ª, extensão nua → 7ª implícita, `4`→sus4, `5±`→slot da quinta.
- [x] 3.3 Derivar `category` (4 categorias Chediak) e `pitch_classes` dos slots.
- [x] 3.4 Testes de slots: `C7(#11)` (5J + #11), `G7sus4` (third=sus4, m7),
      `C6` (sem 7ª), `C/Bb` (bass=7ª).

## 4. `realize()` deriva do parse
- [x] 4.1 Reimplementar `realize()` sobre `ParsedChord`.
- [x] 4.2 Baixo invertido entra nos pcs (`C/Bb` inclui Bb).
- [x] 4.3 Rodar a bateria (tarefa 1) — 0 erros.

## 5. Detecção (`cifra-core`)
- [x] 5.1 Estender `ChordPattern` para `±`, *power chords* (`C5`) e
      desambiguar `/dígito` (tom add) de `/nota` (baixo): `C6/9` inteiro.
- [x] 5.2 Testes de extração com os símbolos do corpus.

## 6. Fase 1 — `Chord` delega
- [x] 6.1 Reescrever os internos de `domain/chord.py` derivando do parse;
      manter `.symbol/.root/.quality/.is_minor/.is_dominant_seventh/.properties`.
- [x] 6.2 `quality` legado derivado da categoria; expor `suspended`/`power`.
- [x] 6.3 Suíte completa (`make test`) verde; medir diferença de análise no corpus.

## 7. Fase 2 (follow-up, pode virar outra change)
- [x] 7.1 Promover `ParsedChord` para `cifra_core.theory`; `Chord` e `realize`
      derivam dele.
