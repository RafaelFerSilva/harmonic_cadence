## Why

A detecção de modo de igreja (`detect_mode`) está **promovida ao caminho de produção**
— alimenta a seção pública "Análise modal" (Centro modal) dos relatórios — mas mente.
Sondagens sobre o corpus GOLD (n=60, raspado ao vivo) mais o corpus sintético offline
mostram:

- `detect_mode` cru retorna **"phrygian" em 53/60** músicas. A causa: `_collection()`
  une **todas** as alturas de **todos** os acordes (sopa quase cromática em harmonia
  rica de MPB), e o ramo frígio (`has(3) and has(1)`, o mais permissivo) sempre vence.
- O gate `_mode_refines_key` filtra para **12/60**, mas guarda **exatamente os errados**:
  todos os 12 são "frígio" sobre tônica menor (Wave Dm, Corcovado Am, Insensatez Bm,
  Chega Dm, Construção Em, Valsinha Cm, As Rosas Dm, Lilás Em, Açaí Bm, Cajuína Cm,
  Nada Será Dm, Canto de Ossanha Dm) — peças **eólias/menor-tonais comuns, nenhuma
  frígia de verdade**. As plausivelmente modais (Sozinho mixo, Tempo Rei dórico, Nem Um
  Dia lídio) são filtradas pelo gate porque o `detect_key` discorda. Saída pública:
  **12 rótulos "Centro modal: X frígio" errados, zero modo real capturado**.

Não há conserto barato. Duas correções in-place foram testadas e **reprovadas**:
(1) exigir a cadência modal característica → corpus sintético regride 8/8→3/8 e ainda
restam 6 falsos no GOLD; (2) coleção só das fundamentais → regride 8/8→2/8 e ainda
restam 10 falsos (+ mixolídios novos espúrios). A nota característica mora no 3º/7º do
acorde, então "só fundamentais" perde a escala; a união completa é cromática. Separar
modo×tonal de fato exige um **corpus de MPB modal curado** e um **discriminador
modal↔tonal principiado** — os mesmos ingredientes que faltam e travam o Incremento 3b.

O caminho honesto: **parar de emitir a mentira agora** (risco zero, não toca detecção
de tonalidade) e **preservar a biblioteca modal** (campo, cadências, tabelas Chediak —
corretas por construção) para uma change futura propriamente escopada.

## What Changes

- **Remover a promoção de `detect_mode` no pipeline** (`analysis_service`): a seção
  "Análise modal" (Centro modal) deixa de ser populada e, por consequência, de
  renderizar nos relatórios Markdown/HTML e no prompt de explicação. O gate
  `_mode_refines_key` e a fusão modo→tonalidade saem com ela.
- **Remover o campo morto `KeyEstimate.church_mode`** (setado em `key_detection.py`,
  lido só por teste) e seu preenchimento.
- **Manter intacta a biblioteca modal**: `detect_mode` como função pura (validada em
  cadências limpas), `modal_field`, `modal_degree`, `modal_cadences`,
  `CHARACTERISTIC`/`MODAL_CADENCE`/`CHARACTERISTIC_NOTE`/`MODAL_CADENTIAL`/`MODAL_AVOID`,
  `church_mode_pt` (PT-BR). `HarmonicAnalysis(church_mode=...)` continua aceitando o
  parâmetro (default `None`); só deixa de ser alimentado pelo pipeline.
- **`ROADMAP.md`**: registrar `fix-or-remove-church-mode` como o **desbloqueador
  honesto** do 3b — remove a mentira ativa; a detecção modal real fica para uma change
  futura (corpus modal MPB + discriminador modal↔tonal).

**NÃO toca:** `detect_key`, `segment_keys`, `TIE_BAND`, a métrica de tonalidade nem o
baseline — zero risco de regressão. As métricas modo/exata/relativa/coleção ficam iguais.

## Capabilities

### New Capabilities

*(nenhuma)*

### Modified Capabilities

- `modal-tonal-center`: a classificação de modo deixa de ser **aplicada
  automaticamente** ao centro tonal a partir da coleção de uma música real (gerava
  falsos frígios); permanece como capacidade de **biblioteca** validada em cadências
  limpas (campo, graus, cadências e tabelas Chediak intactos). O requisito do gate
  "um modo refina, nunca sobrepõe" é aposentado junto com a promoção.

## Impact

- `packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py` —
  remove a chamada/gate/fusão de `detect_mode` (~333-342) e a seção `_modal`
  (~436-463); `mode_info` deixa de existir no fluxo.
- `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py` — remove o
  campo `church_mode` do `KeyEstimate` e seu preenchimento.
- `packages/harmonic_analysis/tests/test_key_mode.py` — removido (testa o campo morto).
- Possível ajuste em `test_reports_sections`/`test_tier2_integration` se assertam a
  seção modal ativa (verificar na implementação).
- **Preservados:** `domain/modal.py`, `presentation/labels.py` (`church_mode_pt`),
  `domain/harmony.py` (param `church_mode`), `test_modal*.py` (corpus/cadential/field).
- `ROADMAP.md` — Incremento 3b: nota de desbloqueio + escopo da change futura.
