## Why

A harmonia tonal-funcional é o padrão da música ocidental e o eixo canônico do nosso
sistema. Depois de `fix-or-remove-church-mode`, somos puramente tonal-funcionais — toda
peça é lida como maior/menor com função T/SD/D. Mas a MPB tem **coloração modal real**
(baião mixolídio, dórico, frígio nordestino) que hoje some da leitura: aparece só como
empréstimos isolados, sem afirmar o padrão.

O ponto-chave: o sistema **já computa a evidência**. A análise funcional rotula
empréstimo modal por acorde — `harmony.py` marca bVII7 como **"Emp"** (subdominante
menor, Chediak); `describe_modal_borrowing` nomeia a origem; `constants.py` tagueia
progressões `(I,bVII,IV,V)`=mixolídio, `(I,bIII,IV,V)`="Modal nordestina". **Falta só
agregar** esses empréstimos num resumo de coloração no nível da peça.

A reintrodução é tonal-**ortodoxa**: a coloração é um **overlay descritivo**, ancorado na
tônica do `detect_key`, que NUNCA altera tom/modo/grau/função. É o oposto exato do
detector removido (que re-centrava sobre a coleção cromática e substituía o eixo —
disparava frígio em 53/60). Aqui não há re-centragem nem substituição: só um resumo, ao
lado, da evidência que a própria análise tonal já produziu.

## What Changes

- Nova anotação **`modal_coloring`** derivada da análise funcional já existente, ancorada
  na tônica tonal, com gatilhos **assimétricos** calibrados contra o ground-truth de
  Chediak (pp. 124-127): **mixolídio (só sobre maior)** por `bVII→I`, bVII recorrente, ou
  **v menor** recorrente (Chediak: I7/Vm7/bVII7M); **frígio (só sobre menor)** pela
  cadência estrutural `bII→i` (≥2). Nunca por uma alteração única de passagem.
- **Modos v1:** mixolídio (sobre tom maior) e frígio (sobre tom menor). **Dórico fica
  fora** — compartilha coleção com o mixolídio, então separá-los exige detecção de centro
  modal (3b, bloqueado); o sinal "IV maior" sozinho dispara falso em eólias com dominantes
  secundários.
- **Saída:** campo estruturado `modal_coloring = {flavor, evidence[], where}` + uma linha
  PT-BR no relatório ("Coloração modal: traços mixolídios (bVII→I em 2 pontos)").
  Subordinada à seção tonal; **omitida por padrão** (a maioria das peças não tem
  coloração).
- **Estritamente aditivo:** o rótulo "Emp" por acorde segue como verdade tonal-funcional;
  `modal_coloring` é só o resumo no nível da peça quando os empréstimos formam um padrão.
- **`ROADMAP.md`:** registrar como a reintrodução tonal-ortodoxa do modalismo (overlay,
  não eixo) — distinta e independente do 3b (detecção de centro modal, ainda bloqueado).

**NÃO toca:** `detect_key`, `segment_keys`, `TIE_BAND`, as funções T/SD/D, nem a
taxonomia de cadência. Baseline de tonalidade **idêntico**.

## Capabilities

### New Capabilities

- `modal-coloring`: a anotação descritiva, no nível da peça, que resume os empréstimos
  modais já detectados num padrão de coloração (mixolídio/frígio/dórico), ancorada na
  tônica tonal, sem alterar a análise tonal-funcional.

### Modified Capabilities

- `analysis-reporting`: os relatórios passam a renderizar a seção/linha de coloração
  modal quando presente, e a omitem graciosamente quando ausente (o caso comum).

## Impact

- **Novo** `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_coloring.py` —
  a regra de agregação (lê a sequência de graus/funções já produzida, ancorada na tônica;
  reusa `modal.py`: `MODAL_CADENCE`, `characteristic_degree`, `modal_cadences`).
- `services/analysis_service.py` — wiring em `_add_depth_sections` (Camada 2), ao lado das
  outras seções, consumindo a análise funcional já computada; emite `modal_coloring`
  (default `None`).
- `presentation/reports/markdown.py` + `html.py` + `explain/prompt.py` — render da linha;
  `presentation/labels.py` — rótulos PT-BR (reusa `church_mode_pt`).
- **Testes:** unidade da regra de gatilho (cadência/recorrência, ancorada); ground-truth
  mínimo (peças MPB curadas com coloração real → dispara); anti-regressão (silêncio nas
  ex-frígias eólias: Wave, Corcovado, Insensatez, Chega…); paridade do baseline.
- **NÃO toca** a detecção de tonalidade nem a `modal-tonal-center` (biblioteca preservada,
  reusada como leitura).
