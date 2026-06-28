## Context

`detect_mode` (`domain/modal.py`) classifica um modo de igreja a partir da coleção
diatônica e do centro tonal. O `analysis_service` o chama (`~333`), arbitra com
`_mode_refines_key` (`~337`) e, se passar, funde modo→tonalidade e popula a seção
"Análise modal" (`_modal`, `~439-463`), renderizada em Markdown/HTML e no prompt.

Em entrada limpa o classificador acerta (corpus sintético `test_modal_corpus` 8/8). Em
músicas reais ele falha: `_collection()` une todas as alturas de todos os acordes →
sopa cromática → o ramo frígio (`has(3) and has(1)`) dispara em quase tudo.

Medições (probes em `scratchpad/`, GOLD n=60 ao vivo):

```
detect_mode cru:     phrygian 53/60 · None 4 · mixolydian 1 · lydian 1 · dorian 1
passa _mode_refines_key: 12/60 — TODOS "phrygian" sobre tônica MENOR (eólias reais)
  Wave Dm · Corcovado Am · Insensatez Bm · Chega Dm · Construção Em · Valsinha Cm
  As Rosas Dm · Lilás Em · Açaí Bm · Cajuína Cm · Nada Será Dm · Canto de Ossanha Dm
modos plausíveis (Sozinho mixo, Tempo Rei dórico, Nem Um Dia lídio): FILTRADOS
```

A seção pública afirma "Centro modal: X frígio" para 12/60, sempre errado.

## Goals / Non-Goals

**Goals:**
- Parar de emitir a classificação modal falsa no relatório (12/60 → 0).
- Preservar a biblioteca modal correta-por-construção para uso futuro.
- Risco zero sobre a detecção de tonalidade e o baseline.

**Non-Goals:**
- Consertar `detect_mode` para músicas reais (provado não-trivial; exige corpus modal
  + discriminador — Incremento 3b, bloqueado).
- Mexer em `detect_key`/`segment_keys`/`TIE_BAND`/métricas de tonalidade.
- Remover a teoria modal (campo, cadências, tabelas Chediak) — ela fica.

## Decisions

### D1 — Remover a **promoção**, não a biblioteca

`analysis_service` deixa de chamar `detect_mode`; somem o gate `_mode_refines_key`, a
fusão modo→tonalidade e a seção `_modal`. `modal.py` inteiro permanece como biblioteca
pura (testado por `test_modal_corpus`/`_cadential`/`_field`). É a fronteira exata entre
"mentira em produção" (sai) e "teoria correta" (fica).

### D2 — A seção "Análise modal" some por **ausência**, não por flag nova

Com `mode_info` fora do fluxo, `modal_analysis` fica sempre `None`. A spec
`analysis-reporting` já manda **omitir** a seção quando `None` ("Tonal piece without
modal analysis") — logo nenhum código de relatório muda; a seção simplesmente nunca
aparece. Sem opt-in nem flag: reintroduzir modalismo será a change futura que traz o
discriminador, e ela reescreve este requisito.

### D3 — Remover o campo morto `KeyEstimate.church_mode`

O campo (`key_detection.py:55`, preenchido `:233-236`) é lido só por `test_key_mode.py`;
nenhum relatório o consome (o caminho de produção usa a chamada própria do
`analysis_service`). É código morto — sai com o teste que o exercita.

### D4 — `HarmonicAnalysis.church_mode` fica, dormente

O param `church_mode` de `HarmonicAnalysis` (usado em `harmony.py:213-224` para rotular
graus diatônicos ao modo) **permanece**, com default `None`. Antes só era alimentado
quando o gate passava; agora nunca é — vira dormente, não morto (a assinatura e a lógica
seguem válidas para a change modal futura). Removê-lo seria escopo extra sem ganho.

### D5 — Por que não tentar mais um conserto do gate

Testar uma terceira via (apertar o gate exigindo a cadência modal) ainda deixa **6/60
falsos frígios** (Corcovado, Chega, Lilás, Açaí, Nada Será, Canto de Ossanha) e
regride o corpus limpo. Nenhuma variante de uma-linha converge. Adiar para quando
houver corpus+discriminador é a decisão honesta, não a preguiçosa.

## Risks / Trade-offs

- **Trade-off: perde-se a aspiração de exibir modo automaticamente.** Mas hoje ela só
  exibe erro; remover não perde nenhum acerto real (eram zero). Ganho líquido de
  honestidade.
- **Risco: testes de integração que assumam a seção modal ativa.** Mitigação: rodar a
  suíte; ajustar `test_reports_sections`/`test_tier2_integration` se afirmarem a
  presença da seção (a expectativa correta passa a ser ausência/omção).
- **Risco: a spec `modal-tonal-center` encolhe.** É intencional e documentado: o
  requisito de classificação aplicada e o do gate saem; os de campo/cadência/tabelas
  (biblioteca) ficam. A change futura de modalismo real reescreve a parte aplicada.
