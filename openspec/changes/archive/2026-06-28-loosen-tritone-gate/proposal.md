## Why

O gate de qualidade do trítono (Fase B 3b) corrige um V detectado como tônica, mas só
quando o centro do K-S aparece **exclusivamente** como dominante-7. Essa condição é
restritiva demais: nos 4 casos residuais de V-como-tônica (A Banda, Apesar de Você,
Menino do Rio, Aquele Abraço), o V detectado (A, A, C, A) aparece *também* como acorde de
repouso ocasional (A maior ×9, C maior ×5), então o gate aborta — mesmo havendo um V7/SubV
**funcional** resolvendo na tônica real em posição estrutural. É o "buraco de centro"
diagnosticado no baseline (centro 79%, 15/19).

Uma sondagem ao vivo + simulação contra todo o corpus (read-only, antes de qualquer código)
mostrou que um segundo caminho, **centrado no alvo de resolução** em vez da pureza do V,
corrige 3 dos 4 (A Banda, Apesar, Menino do Rio) com **zero regressão das corretas** — o
4º (Aquele Abraço, uma tônica `I7` de funk) fica de fora, sem piorar.

## What Changes

- Adicionar ao gate de qualidade um **segundo caminho (ancorado por resolução)**: corrige
  o centro K-S `Y` para `X = (Y − 7) mod 12` quando — mesmo que `Y` apareça como repouso
  ocasional — **todas** valem: (a) um V7/SubV **funcional** (trítono real) resolve em `X`
  em posição estrutural/final (o mesmo critério de `verify_tonal_center`); (b) `X` é o
  **repouso predominante** da peça (acordes com raiz `X` são majoritariamente maj/min,
  contagem ≥ 2); (c) `X` é **âncora estrutural** (primeiro ou último acorde); (d) `X ≠ Y`.
- O **caminho restrito existente** (Y exclusivamente dominante → corrige) permanece
  intacto, assim como os guards: blues sem repouso aborta, dim7 inelegível, tônica que
  descansa nunca é rebaixada.
- O afrouxamento **não toca** a TIE_BAND, a corroboração cadencial, a correção de modo
  paralelo, nem a segmentação de modulação.

## Capabilities

### New Capabilities
<!-- Nenhuma: estende uma capability existente. -->

### Modified Capabilities
- `key-detection`: o requisito do gate de qualidade do trítono ganha um segundo caminho
  (ancorado por resolução), preservando o caminho restrito e todos os guards.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/key_detection.py`
  (`_tritone_gate` — adicionar o caminho ancorado, reusando o histograma de categorias e a
  lógica de resolução por baixo já presentes). Testes em `test_tritone_gate.py`.
- **Efeito medido (simulação read-only sobre o corpus):** corrige **A Banda** (A→D),
  **Apesar de Você** (A→D), **Menino do Rio** (C→F); **0 regressões** das corretas; 1 troca
  de erro por erro neutra (Esquinas, A→D, ambos ≠ F — não muda exata nem coleção). Projeção:
  tônica-exata **69% → 74%**, centro estrutural **79% → 95%** (15/19 → 18/19), modo e
  coleção **idênticos**.
- **Fora do alcance (consciente):** Aquele Abraço (tônica `I7` de funk: a tônica real
  aparece como dominante e o IV parece repouso) — caso distinto, não atacado aqui.
- **Trava inegociável:** `scripts/key_baseline.py` ao vivo + suíte completa antes de
  arquivar; zero regressão das corretas (a regra que já barrou 2 ships nesta mesma frente).
