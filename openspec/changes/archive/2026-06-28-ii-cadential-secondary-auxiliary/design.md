## Context

A change irmã (`dominant-auxiliary-and-secondary-subv`, arquivada) classificou os dominantes pelo alvo (diatônico=secundário, empréstimo=auxiliar). O II cadencial (Chediak XIX, p.100) é o **iim7 que prepara** esses dominantes, classificado pelo **mesmo eixo do alvo**. Sondagem ao vivo: `Dm7 G7→C` (primário) → `SD`; `F#m7 B7→Em` (secundário) → `Emp` (errado); `Am7 D7→G` → `T`; `Cm7 F7→Bb` (auxiliar) → `T`. O código `D2` ("Segunda Cadencial") existe mas está **morto** — `SD.degrees` lista `ii`/`iim7` e é alcançado antes no laço da seção 1.

Camada de função (não toca `detect_key`) → baseline idêntico; a trava é a suíte. Há um ponto de atenção: o primário muda de `SD` para `D2`.

## Goals / Non-Goals

**Goals:**
- Reconhecer o II cadencial (menor + dominante 4ªJ acima) e classificá-lo primário/secundário/auxiliar pelo alvo do dominante.
- Tirar o secundário/auxiliar de `Emp`/`T`.

**Non-Goals:**
- Critério de **tempo forte** (Chediak) — as cifras não têm metro; usa-se a relação harmônica.
- II-V's encadeados/estendidos (XXVIII) — change futura.
- Tocar a classificação do próprio dominante (já feita na change XVIII).

## Decisions

### D1 — Detecção pelo par `iim7 → V` (4ªJ ascendente)

Um ramo novo: `chord.is_minor` e `next_chord.is_dominant_seventh` e `interval(chord.root, next.root) == 5`. O `target = (next.root + 5) mod 12` é a 5ª justa abaixo da fundamental do V (seu acorde de resolução nominal). *Por quê computar o alvo:* `analyze_function` só vê um acorde à frente; o alvo do V (2 à frente) é **determinado** pela fundamental do V (resolução padrão 5ª abaixo), então não é preciso o acorde físico — evita mudar a assinatura.

### D2 — Classificação pelo alvo, espelhando XVIII

`target == key` → primário; `target ∈ scale_pcs` (diatônico, não-tônica) → secundário; senão → auxiliar. O grau do alvo é nomeado por `_CHROMATIC_DEGREE` (já existe), dando o rótulo `V7/III`, `V7/V`, `V7/bVII`. *Por quê:* é exatamente o critério do Chediak (alvo diatônico vs empréstimo), consistente com a change irmã.

### D3 — Reusar o código `D2`, nome carrega o tipo

Os três usam o código `D2` (revivido para seu propósito), com nome "II cadencial primário/secundário/auxiliar (de V7/x)". *Por quê não novos códigos:* o II cadencial é uma função única (subdominante cadencial) com três sabores; o tipo informativo vai no nome, sem inflar o enum. A descrição cita Chediak p.100.

### D4 — Precedência antes da seção 1

O ramo vem **antes** da leitura diatônica (seção 1) para interceptar `Dm7`(SD), `F#m7`(Emp) e `Cm7`(T). *Risco controlado:* só dispara sob a conjunção estrita (menor + dominante 4ªJ acima), então um iim7 que não precede dominante segue inalterado. O primário `Dm7 G7→C` muda de `SD`→`D2` — validado contra a suíte; se um teste codificava `SD` para esse padrão, ele reflete o comportamento antigo e será ajustado para `D2` (o rótulo fiel ao Chediak).

## Risks / Trade-offs

- **[`Dm7 G7→C` muda de SD para D2]** → é a leitura fiel (II cadencial). A trava é a suíte; reviso qualquer teste que dependa do `SD` antigo. Progressões por função (`detect_progressions`) podem mudar — verifico os testes de progressão.
- **[Falso II cadencial sem tempo forte]** → a conjunção (menor + V 4ªJ acima) é específica; sem metro, é o melhor sinal. Documentado.
- **[Alvo deceptivo (V não resolve no alvo nominal)]** → o II cadencial é caracterizado pela relação ii-V, não pela resolução efetiva; o tipo usa o alvo nominal do V (fiel ao Chediak).
- **[Baseline]** → impossível regredir (`detect_key` intacto); rodo como sanidade.

## Migration Plan

1. Adicionar o ramo de II cadencial antes da seção 1; remover o ramo `D2` morto da seção 2.
2. Testes: primário (`Dm7 G7`), secundário (`F#m7 B7`, `Am7 D7`), auxiliar (`Cm7 F7`, `Bbm7 Eb7`), e o guard (menor sem dominante 4ªJ acima).
3. `make test` + `make lint`; `scripts/key_baseline.py` (idêntico). Atualizar ROADMAP.
4. Rollback = remover o ramo e restaurar o `D2` da seção 2.

## Open Questions

- Exigir 7ª no acorde menor (`m7`) ou aceitar tríade menor? Chediak fala "acorde menor"; aceito menor (com ou sem 7ª) e deixo o rótulo genérico. Refinável se gerar ruído.
