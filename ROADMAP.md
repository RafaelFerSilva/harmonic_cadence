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
- **Corpus de validação ampliado** — `widen-key-corpus` (+ leva 2): baseline de n≈6
  para **n=60**, ouro = tom do **próprio Cifra Club** (independente, sem gap de
  transposição → tônica-exata honesta). Fatos `(artista, música, tom)`; cifras não
  armazenadas. (Chediak segue como árbitro **teórico**, não como gold de baseline.)
- **Fase B v1 — desempate cadencial** — `tonal-center-detection`: um estágio de
  corroboração cadencial desempata candidatos em quase-empate do K-S usando o centro
  tonal funcional (1º acorde, acorde final, cadência autêntica V/SubV → tônica, com o
  **baixo** como âncora). Resolve a confusão **relativa** (maior↔relativa menor).
- **Fase B v2 — correção de modo paralelo** — `parallel-mode-correction`: na tônica
  âncora, inverte o **modo** quando a qualidade dos acordes de tônica contradiz o K-S
  (a cadência não distingue paralelas — a dominante é comum). Resolve a **paralela**
  (Wave/Chega/Valsinha). Conservador (gate de âncora-baixo); Sina e gate sintético
  intactos.

**Baseline de detecção de tonalidade** (`uv run python scripts/key_baseline.py`,
ouro = tom do Cifra Club, **n=60**, com a Fase B v1+v2): **modo 83% · tônica exata
62% · relativa-consciente 72%** (K-S puro era 64/46/61; v1 só, 67/50/62). A v1
generalizou (validada quase held-out nas 32 músicas novas: 66/50/62 ≈ in-sample). Sem
gap de transposição, a tônica-exata é honesta.

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

As v1 (relativa) e v2 (paralela) estão no `main` e levaram o modo de 64% para **83%**.
Os incrementos seguintes, **medindo cada um contra o baseline** e sem quebrar a
arbitragem modo↔tom nem o gate sintético:

1. **Segmentação das modulações reais** (*Wave*, *Chega de Saudade*: começam menor,
   terminam maior) — rótulo único sempre erra; usar `segment_keys`, não a estimativa
   pontual. **Nota honesta:** a v2 "acerta" o gold dessas invertendo p/ menor, mas a
   leitura correta é multi-região. É medição/apresentação, não detecção.
2. **Tunar/afrouxar o EPS da banda** (agora com n=60) — pegaria casos relativos ainda
   fora da banda (*Papel Marché*, gap ~0.07) sem in-sample chasing.
3. **Casos residuais** — *Esquinas*/*Lilás*/*Açaí* (Djavan, harmonia modal complexa),
   e a tônica de modos de igreja pelo K-S (`G F C G` lido como Dó maior).

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
| 1 | Segmentar modulação real (Wave/Chega) na apresentação | `modulation-regions` | M |
| 2 | Afrouxar/tunar o EPS da banda (agora com n=60) | `tune-tie-band` | S |
| 3 | Casos residuais (Djavan modal; tônica de modos) | — | M |

_Concluídos: `enharmonic-spelling`, `consolidate-modal-field` (em
`finish-note-spelling`), `widen-key-corpus` + leva 2 (n=60), `tonal-center-detection`
(Fase B v1, relativa), `parallel-mode-correction` (Fase B v2, paralela; modo
64%→83% acumulado)._

## Contexto de fonte (copyright)

Autoridade: **Almir Chediak, *Harmonia e Improvisação* Vol. I** (`base_estudo/`,
gitignored). Usamos **fatos** (convenções, tonalidades das músicas analisadas) —
nunca o texto, as tabelas-como-diagramadas, nem as cifras das 70 músicas. Os
acordes vêm do Cifra Club; o `scripts/key_baseline.py` guarda só a lista de
músicas + o tom anotado pelo **próprio Cifra Club** (fatos públicos), não as
cifras — corpus independente da Parte 4 do livro.
