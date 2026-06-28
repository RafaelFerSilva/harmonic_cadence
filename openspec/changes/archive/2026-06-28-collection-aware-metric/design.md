## Context

O harness (`key_accuracy.py`) compara o tom **detectado** com o **anotado** (gold = tom do Cifra Club) com três métricas: modo, tônica-exata e relativa-consciente. A relativa-consciente perdoa só a confusão **maior↔vi (relativa menor)** — a lição da Sina, fechada na Fase B v1.

A investigação do Incremento 3 (varredura do corpus n=60, ver `scratchpad/inc3_probe.py`) revelou que as falhas restantes não são um único tipo: a tônica detectada cai em **vários graus diatônicos do gold** — V (6×), vi (4×), iii (3×), IV (2×). Só 2 casos (Desafinado, Começar) erram a coleção de fato. Falta uma métrica que conte essa distinção.

## Goals / Non-Goals

**Goals:**
- Medir, como 4ª métrica, se a tônica detectada pertence à **coleção diatônica** do gold (≈ armadura de clave).
- Reportá-la ao lado das três existentes, no harness e no baseline, com verdict por música.
- Tornar honesto o relato de acurácia: separar erro de coleção (raro) de erro de centro (comum, difícil).

**Non-Goals:**
- Alterar `detect_key`, `segment_keys`, `TIE_BAND`, `modal.py` ou qualquer lógica de detecção.
- Substituir ou afrouxar a métrica de tônica-exata (continua o número de primeira classe).
- Implementar arbitragem modal↔tonal de centro (3b) — fora de escopo, bloqueado.

## Decisions

### D1 — `same_collection` mede pelo **offset da tônica**, ignorando o rótulo maior/menor detectado

A coleção do gold é o conjunto de offsets diatônicos da sua escala:
- gold maior → `{0, 2, 4, 5, 7, 9, 11}` (T-T-S-T-T-T-S a partir da tônica)
- gold menor → `{0, 2, 3, 5, 7, 8, 10}` (menor natural)

`same_collection(gold, detected)` = `(det_pc - gold_pc) % 12 ∈ offsets(gold)`.

Ignora deliberadamente o modo (maior/menor) do detectado, porque ele é **não-confiável em peça modal**: o K-S rotula "E menor" para uma peça em E frígio (cuja coleção é a de C maior). O que importa para "armadura certa" é só a posição da tônica detectada dentro da escala do gold.

```
Exemplo — Lilás (gold C maior, detectado E menor):
  (4 - 0) % 12 = 4  ∈ {0,2,4,5,7,9,11}  → same_collection = True (E = grau III)
Exemplo — Começar (gold A maior, detectado C maior):
  (0 - 9) % 12 = 3  ∉ {0,2,4,5,7,9,11}  → same_collection = False (coleção errada)
```

Alternativa descartada: parear pela relativa-maior (`minor→tonic+3`). Falha para peças modais — a relativa-maior de "E menor" é G, não C, e daria a coleção errada para um E frígio cuja coleção real é C.

### D2 — A 4ª métrica é **aditiva**, não substitui nenhuma

`collection_accuracy` entra como chave nova em `evaluate_corpus`; as três existentes ficam intactas. O baseline ganha uma 4ª linha. Isso preserva a tônica-exata como métrica honesta de primeira classe e só acrescenta contexto.

### D3 — Invariante de aninhamento verificada por teste

Por construção, `exata ⊆ relativa-consciente ⊆ coleção`:
- exata: offset 0 e mesmo modo.
- relativa-consciente: exata ∪ {vi} (offset 9 com troca maior→menor / 3 menor→maior).
- coleção: todos os offsets diatônicos (inclui 0 e 9 e 3 e os demais).

Cada nível é mais permissivo que o anterior, então as taxas obedecem `exact ≤ relative_aware ≤ collection`. Um teste no corpus sintético trava essa invariante.

### D4 — Verdict por música no baseline reusa a hierarquia existente

A função de verdict do `key_baseline.py` ganha um nível antes do "ERRO": se não é exato/relativo/modo-ok mas `same_collection` é True, o verdict vira **"coleção"** (acertou a armadura, errou o centro). "ERRO" passa a significar **coleção errada de fato** — o erro caro e raro.

## Risks / Trade-offs

- **Risco: a métrica de coleção é permissiva demais (perdoa 7 de 12 tônicas).** Mitigação: ela é reportada **ao lado**, nunca no lugar, da tônica-exata. O valor é diagnóstico — provar que o resíduo é "centro dentro da coleção", não "detector quebrado" —, não inflar o headline. O ROADMAP deixa o enquadramento explícito.

- **Trade-off: não melhora a detecção.** É o ponto: 3a é medição honesta. A melhoria de centro (3b) está bloqueada por falta de discriminador modal e é registrada como tal.

## Open Questions

- O `church_mode`/`detect_mode` (frígio em 52/60) deve ser consertado ou removido da saída pública? Fica como item separado no ROADMAP — não é escopo desta change.
- Vale ampliar o corpus com mais peças modais explícitas (Edu Lobo *Arrastão* dórico, Gil *Procissão* mixolídio) para tensionar a métrica? Deferido.
