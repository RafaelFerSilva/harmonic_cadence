## Why

A detecção de tonalidade erra a tônica exata em 19/60 músicas do corpus, mas a investigação do Incremento 3 mostrou que **~17 dessas 19 falhas têm a tônica detectada num grau diatônico do tom-gold** (V em 6 casos, vi em 4, iii/mediante em 3, IV em 2). O detector acerta a vizinhança diatônica (≈ a armadura de clave) ~95% das vezes, errando só o **centro tonal dentro dela**.

As 3 métricas atuais não expõem isso: a relativa-consciente só perdoa **vi** (relativa menor), não os outros graus. Sem uma 4ª métrica, o número "tônica exata 67%" sugere um detector mais fraco do que ele é, e não separa o erro **caro e raro** (coleção errada: só Desafinado +10 e Começar +3 no corpus) do erro **comum e difícil** (centro errado dentro da coleção certa — parte subjetivo, dependente do viés tonal do próprio gold do Cifra Club).

A correção de **detecção** (3b — arbitragem modal↔tonal de centro) fica **fora de escopo**: os discriminadores que ela exigiria não existem com precisão. `detect_mode` retorna "phrygian" em 52/60 músicas (inclusive nas exatas-corretas), é ruído. A falha se espalha por V/vi/iii/IV sem conserto único, e cada gate arriscaria as 41 corretas. O critério do Chediak que separaria mediante de mixolídio (resolução de dominante funcional, pp. 121-123) não é implementável de forma confiável hoje.

## What Changes

- `validation/key_accuracy.py`: nova função `same_collection(gold, detected)` — True se a tônica detectada é um grau diatônico da escala do gold (offset `(det_pc - gold_pc) % 12` ∈ conjunto diatônico do gold; maior `{0,2,4,5,7,9,11}`, menor natural `{0,2,3,5,7,8,10}`). Ignora o rótulo maior/menor do detectado (não-confiável em peça modal — "E menor" detectado para E frígio).
- `KeyEval` ganha o campo `same_collection: bool`; `evaluate_song` o preenche.
- `evaluate_corpus` agrega `collection_accuracy = sum(same_collection) / n`.
- `scripts/key_baseline.py`: imprime a 4ª linha "coleção (armadura): NN%" e um verdict por música ("coleção" quando acerta a coleção mas erra o centro).
- `ROADMAP.md`: 3a registrado como feito; 3b explicitamente **bloqueado** por falta de discriminador modal preciso; `church_mode`/`detect_mode` anotado como candidato a conserto/remoção separado.

## Capabilities

### New Capabilities

*(nenhuma)*

### Modified Capabilities

- `key-accuracy-evaluation`: adiciona a 4ª métrica (coleção-consciente / armadura de clave) ao harness e ao baseline, com a invariante de aninhamento das métricas.

## Impact

- `packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py` — `same_collection`, campo em `KeyEval`, agregação em `evaluate_corpus`.
- `scripts/key_baseline.py` — 4ª linha de métrica e verdict por música.
- Testes: casos unitários para `same_collection` (graus diatônicos vs cromáticos, gold maior e menor) e a invariante de aninhamento `exata ⊆ relativa-consciente ⊆ coleção`.
- **NÃO toca:** `detect_key`, `segment_keys`, `TIE_BAND`, `modal.py` — zero risco de regressão na detecção.
