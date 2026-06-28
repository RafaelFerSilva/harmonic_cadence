## 1. Regra de agregação (domain/modal_coloring.py)

- [x] 1.1 Criar `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_coloring.py` com `detect_coloring(key_note, mode, chords|degree_seq) -> Optional[dict]`, ancorado na tônica tonal. A evidência vem dos acordes relativos à tônica do detect_key (offset + qualidade maior/menor), nunca de re-centragem.
- [x] 1.2 Mixolídio (SÓ tom maior): sinais não-diatônicos = bVII maior e v menor. Dispara se bVII→I (≥1) OU bVII distinto ≥2 OU v-menor distinto ≥2. (Chediak I7/Vm7/bVII7M, p. 124; Vm pega Upa Neguinho.)
- [x] 1.3 Frígio (SÓ tom menor): dispara só pela cadência estrutural bII→i ≥2. bII pontual/recorrente-sem-cadência NÃO dispara (é napolitano/SubV tonal).
- [x] 1.4 Dórico e demais: NÃO emitir na v1. Contagem por ocorrências DISTINTAS (colapsa repetição de seção). Retornar `{"flavor", "evidence": [str], "where": [...]}` ou `None`; flavors só em {mixolydian, phrygian}.

## 2. Wiring no pipeline (analysis_service.py)

- [x] 2.1 Em `_add_depth_sections`, após os graus/funções já computados, chamar `detect_coloring` com a tônica/modo tonais e a sequência de graus; emitir `result["modal_coloring"]` (default `None`).
- [x] 2.2 Garantir que NÃO altera `key`/`mode`/`harmonic_analysis`/`cadences` — puramente aditivo; usar `_safe_section` para degradar visível em falha.

## 3. Apresentação (relatórios + PT-BR)

- [x] 3.1 Em `presentation/labels.py`, rótulo PT-BR do flavor (reusar `church_mode_pt`: mixolydian→mixolídio, phrygian→frígio, dorian→dórico).
- [x] 3.2 Em `presentation/reports/markdown.py` e `html.py`, renderizar a linha "Coloração modal: traços <modo> (<evidência>)" quando `modal_coloring` presente; omitir quando `None`. Subordinada à seção tonal, nunca substituindo o cabeçalho tom/modo.
- [x] 3.3 Em `explain/prompt.py`, incluir a coloração no prompt de explicação quando presente.

## 4. Testes (offline, sintéticos por modo)

- [x] 4.1 Unidade do gatilho (`test_modal_coloring.py`): mixolídio por bVII→I (maior); mixolídio por v-menor recorrente (maior, ex. progressão estilo Upa Neguinho: I–Vm–I); frígio por bII→i ≥2 (menor); ancoragem (bII em Am → frígio relativo a A, sem re-centrar).
- [x] 4.2 Ausência/assimetria: bVII em tom MENOR → `None` (diatônico eólio); bII único/sem-cadência em menor → `None` (mas rótulo SubV/Emp no acorde permanece); IV maior em menor → `None` (dórico fora da v1); maior diatônica (`C F G7 C`) → `None`.
- [x] 4.3 Anti-regressão do falso-positivo: progressões sintéticas equivalentes às eólias do corpus (i-iv-V-i, com bVII diatônico e bII napolitano pontual) → `None`.
- [x] 4.4 Render: relatório com coloração mostra a linha; sem coloração omite; o cabeçalho tom/modo é o tonal em ambos.

## 4b. Validação ao vivo contra o ground-truth de Chediak (rede)

- [x] 4b.1 Rodar uma varredura usando `scripts/modal_coloring_groundtruth.py` (CHEDIAK_GOLD + DATA_VERIFIED + NEGATIVE_CONTROLS): confirmar que dispara nos positivos harmonicamente explícitos (Ponteio mixo; Canto de Ossanha frígio) e SILENCIA nos controles eólios (Wave/Corcovado/Insensatez/Construção).
- [x] 4b.2 Documentar as divergências esperadas vs Chediak (sem "consertar"): Procissão (arranjo tonalizado → silêncio), Arrastão (centro Ré vs Lá dórico → superfície mixolídia), Upa Neguinho (depende do sinal v-menor), Gravidade (lídio b7 fora da v1).

## 5. Validação e ROADMAP

- [x] 5.1 `make test` (todos verdes) e `make lint`.
- [x] 5.2 `uv run python scripts/key_baseline.py` (rede): confirmar baseline de tonalidade IDÊNTICO (a change não toca detecção).
- [x] 5.3 Sanidade ao vivo: rodar a análise de uma peça com bVII recorrente conhecido e conferir a linha de coloração; rodar Corcovado/Wave e confirmar ausência de coloração.
- [x] 5.4 Atualizar `ROADMAP.md`: `modal-coloring-overlay` feito (reintrodução tonal-ortodoxa do modalismo como overlay descritivo, ancorado, aditivo); distinto e independente do 3b (detecção de centro modal, ainda bloqueado).
