## 1. Fixture de fatos do Chediak-ouro estrutural (com proveniência)

- [x] 1.1 Criar `scripts/chediak_structural_gold.py` (molde de `modal_coloring_groundtruth.py`): fatos `(artista, música, cc_key, structural_offset, center_type, modo, provenance, justificativa)`, com `provenance ∈ {chediak, verified, unverified}`. `offset=0` NUNCA é default herdado — só entra como afirmação verificada (chediak/verified).
- [x] 1.2 TIER A (chediak): overrides modais citados da Parte 2 — Arrastão (Ré→Lá dórico, offset 7, p.125), Upa Neguinho (Ré mixo, p.126), Procissão (Dó mixo, p.126), Pra Não Dizer (Mi eólio, p.127). Calcular cada offset do fato (cc_key vs centro Chediak). Reservados como âncora de validação não-circular.
- [x] 1.3 TIER B (verified): para as músicas tonais do n=60, marcar `verified` (offset 0) SÓ quando houver V7 funcional (trítono real) resolvendo no cc_key em cadência estrutural/final — registrar o critério na justificativa (anotação cega: decidir o centro antes de olhar o cc_key). As demais → `unverified`.
- [x] 1.4 Documentar no cabeçalho: muro de copyright (só fatos; Parte 4 só tons citados; nunca harmonizações), a derivação do offset, e a regra de proveniência (cc_key = âncora de transposição, não fonte da verdade do centro).

## 2. Métrica de acerto-de-centro (key_accuracy.py)

- [x] 2.1 Adicionar `center_offset(detected, cc_key) -> int` e `center_ok(detected_pc, cc_key_pc, structural_offset) -> bool` = `(detected_pc - cc_key_pc) % 12 == structural_offset`. Foco na tônica/centro, mode-agnóstico.
- [x] 2.2 Estender `KeyEval` (ou um eval irmão) com `center_ok` e o `structural_offset` usado; `evaluate_song` aceita o offset (default 0 quando não há override).
- [x] 2.3 Em `evaluate_corpus`, agregar `"center_accuracy"` SÓ sobre o subconjunto `chediak`+`verified`; contar `unverified` à parte (cobertura). Aceitar o mapa de proveniência+offset por música.

## 3. Baseline: 5ª linha + verdict de divergência (key_baseline.py)

- [x] 3.1 Importar os overrides de `scripts/chediak_structural_gold.py`; resolver o `structural_offset` por música (0 por padrão).
- [x] 3.2 Calcular `center = sum(center_ok(...)) / n` e imprimir a 5ª linha agregada: `centro (estrutural/Chediak):  NN%`. As 4 linhas Cifra-Club ficam idênticas.
- [x] 3.3 No verdict por música, quando `structural_offset ≠ 0` (Cifra Club ≠ Chediak), marcar `"divergência"` com as duas leituras visíveis.

## 4. Testes

- [x] 4.1 `test_key_accuracy.py`: `center_ok` — invariância a transposição (transpor acordes+cc_key por T não muda o verdict); mediante (offset 0, detectou iii) → miss; modal override (offset 7) → acerto quando detecta o centro certo.
- [x] 4.2 `evaluate_corpus` expõe `center_accuracy` SÓ sobre chediak+verified; `unverified` fica fora do denominador e é contado à parte; divergência aplicada nos modais (Tier A).

## 5. Validação e ROADMAP

- [x] 5.1 `make test` (verde) e `make lint`.
- [x] 5.2 `uv run python scripts/key_baseline.py` (rede): confirmar as 4 linhas Cifra-Club **idênticas** e registrar o **buraco de centro** — quantas das n=60 erram o centro estrutural (mediantes + modais). Documentar os 5 números no ROADMAP.
- [x] 5.3 Atualizar `ROADMAP.md`: `chediak-structural-gold` feito (3b-corpus, 2º ouro + métrica de centro); a change 2 (`tonal-center-tritone-gate`) vai mover esse número sem regredir as 4 métricas Cifra-Club.
