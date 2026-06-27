# Roadmap & Handoff

Princípio que guiou tudo: **fundação antes de produto; derivar em vez de
transcrever; medir em vez de achar.** A teoria do Chediak (Vol. I) está
destilada, implementada e testada; a fronteira agora é **precisão** e
**apresentação** para o público BR.

## Status (2026-06-27)

**Feito e no `main`** (~22 changes OpenSpec, 255 testes verdes, `openspec/`
versionado em `openspec/changes/archive/`):

- **Teoria harmônica destilada do Chediak** — parsing de acorde (dialeto `±`,
  slots, `°`=dim7), função T/SD/D + dom7-sem-função, campos modais derivados,
  as 5 cadências, escala-acorde dos dominantes (incl. alterados), cadenciais/
  evitados por modo. Cada decisão cita a página do livro.
- **Fundação tonal** — `key-mode-arbitration`: um modo só **refina** a
  tonalidade do `detect_key` (mesma tônica E qualidade), nunca a inverte.
  Corrigiu o bug da Sina ("D menor" → "A maior").
- **Localização PT-BR** — relatórios humanos em português (`menor`, `frígio`,
  `mixolídio`, `dominante`); modelo interno em inglês canônico; JSON canônico.
- **Observabilidade** — `_safe_section` + `result["diagnostics"]` + `logging`;
  seções degradam visíveis, não em silêncio.
- **Fase A (medição)** — `capture-song-key` (tom do Cifra Club capturado, antes
  era descartado), `validation-harness` (3 métricas), e o **baseline**.
- **Limpeza & fonte única de nota** — `remove-dead-code` (módulo órfão
  `modal_analysis.py` + ~172 LoC mortas) e `finish-note-spelling`: aposentado o
  subsistema de nota sustenido-só (`MODE_HARMONY`/`MODES`/`NOTE_REPLACEMENTS`/
  `normalize_note`/`guess_key`). Agora **uma** fonte de nota (`Note` soletrada) e
  **uma** detecção de tom (`detect_key`) em todos os entry points; o empréstimo
  modal grafa bemóis corretamente (`Bb`, não `A#`) e passa a identificar acordes
  bemóis (antes "não identificado").
- **Corpus de validação ampliado** — `widen-key-corpus`: baseline de n≈6 para
  **n=28**, ouro = tom do **próprio Cifra Club** (independente, sem gap de
  transposição → tônica-exata honesta). Fatos `(artista, música, tom)`; cifras não
  armazenadas. (Chediak segue como árbitro **teórico**, não como gold de baseline.)
- **Fase B v1 — desempate cadencial** — `tonal-center-detection`: um estágio de
  corroboração cadencial desempata candidatos em quase-empate do K-S usando o centro
  tonal funcional (1º acorde, acorde final, cadência autêntica V/SubV → tônica, com o
  **baixo** como âncora). Conservador (não sobrepõe K-S confiante); a Sina e o gate
  sintético seguem intactos.

**Baseline de detecção de tonalidade** (`uv run python scripts/key_baseline.py`,
ouro = tom do Cifra Club, n=28, **com a Fase B v1**): **modo 68% · tônica exata 50% ·
relativa-consciente 61%** (era 64/46/61 com K-S puro; *Sampa* virou A menor→C maior).
Sem gap de transposição, a tônica-exata é honesta. Restam **duas** confusões: a
**relativa** ainda fora da banda em alguns casos (*Papel Marché*, *O Leãozinho*) e a
**paralela** (mesma tônica, modo trocado: Wave, Chega de Saudade, Valsinha).

## Como rodar

```bash
make test                               # uv run pytest (toda a suíte)
make lint                               # uv run ruff check packages
uv run python scripts/key_baseline.py   # baseline de tonalidade (precisa de rede)
openspec list                           # changes ativas
openspec list --specs                   # capabilities (specs)
```

Fluxo de trabalho: cada melhoria é uma **change OpenSpec** (proposal → design →
specs → tasks → implementar → `openspec archive`). As changes vivem em
`openspec/changes/`, arquivadas em `openspec/changes/archive/AAAA-MM-DD-<nome>`.

## Próximo passo — Fase B, próximos incrementos ⭐

A **v1** (desempate cadencial conservador) está no `main` e subiu o modo para 68%.
Os incrementos seguintes, **medindo cada um contra o baseline** e sem quebrar a
arbitragem modo↔tom nem o gate sintético:

1. **Ampliar o corpus antes de tunar** (n=28 ainda é pequeno) — o EPS da banda foi
   fixado conservador (0.06) de propósito; tunar ou afrouxar só faz sentido com
   corpus maior, senão é in-sample chasing. Casos como *Papel Marché* (gap ~0.07)
   esperam isso.
2. **Override agressivo para a paralela-erro** (*Valsinha*: cadência `G7→Cm` clara,
   mas K-S confiantemente em Dó maior) — deixar a corroboração sobrepor um K-S
   confiante quando o sinal cadencial é forte. Risco de regressão → medir com rigor.
3. **Segmentação das modulações reais** (*Wave*, *Chega de Saudade*: começam menor,
   terminam maior) — rótulo único sempre erra; usar `segment_keys`, não a estimativa
   pontual. É medição/apresentação, não detecção.

Secundário: o K-S não acha a tônica de modos de igreja (`G F C G` → lê Dó maior, não
Sol mixolídio).

## Trilha paralela (contida, encaixa a qualquer momento)

- ~~**Spelling enarmônico**~~ — **feito** em `finish-note-spelling` (Tensão #2
  fechada: empréstimo modal e campo derivado grafam pela `Note` soletrada).
- ~~**Consolidação legada**~~ — **feito** em `remove-dead-code` +
  `finish-note-spelling` (`MODE_HARMONY` e `normalize_note` sustenido-só
  aposentados; fonte única de nota).
- ~~**Ampliar o corpus de validação**~~ — **feito** em `widen-key-corpus` (n=28,
  ouro = tom do Cifra Club). Dá para crescer mais a qualquer momento.

## Sequência sugerida (próximas sessões)

| # | Tema | Change | Tam. |
|---|---|---|---|
| 1 | Ampliar mais o corpus (destrava tunar o EPS com honestidade) | `widen-key-corpus-2` | S |
| 2 | Override agressivo p/ paralela-erro (Valsinha) | `cadence-override` | M |
| 3 | Segmentar modulação real (Wave/Chega) na apresentação | `modulation-regions` | M |

_Concluídos: `enharmonic-spelling`, `consolidate-modal-field` (em
`finish-note-spelling`), `widen-key-corpus` (n=28), `tonal-center-detection` (Fase B
v1: modo 64%→68%)._

## Contexto de fonte (copyright)

Autoridade: **Almir Chediak, *Harmonia e Improvisação* Vol. I** (`base_estudo/`,
gitignored). Usamos **fatos** (convenções, tonalidades das músicas analisadas) —
nunca o texto, as tabelas-como-diagramadas, nem as cifras das 70 músicas. Os
acordes vêm do Cifra Club; o `scripts/key_baseline.py` guarda só a lista de
músicas + o tom anotado pelo **próprio Cifra Club** (fatos públicos), não as
cifras — corpus independente da Parte 4 do livro.
