# Roadmap & Handoff

Princípio que guiou tudo: **fundação antes de produto; derivar em vez de
transcrever; medir em vez de achar.** A teoria do Chediak (Vol. I) está
destilada, implementada e testada; a fronteira agora é **precisão** e
**apresentação** para o público BR.

## Status (2026-06-27)

**Feito e no `main`** (~21 changes OpenSpec, 247 testes verdes, `openspec/`
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

**Baseline de detecção de tonalidade** (`uv run python scripts/key_baseline.py`,
ouro = tom do Cifra Club, n=28): **modo 64% · tônica exata 46% · relativa-consciente
61%**. Sem gap de transposição (ouro e acordes da mesma fonte), a tônica-exata é
honesta. O corpus expõe **duas** confusões sistemáticas: **relativa** (maior →
relativa menor; ~4 casos) e **paralela** (mesma tônica, modo trocado: Wave, Chega
de Saudade, Valsinha; ~5 casos).

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

## Próximo passo — Fase B (centro tonal) ⭐

Alvo **afiado pelo baseline (n=28)**: o K-S erra o **modo** em ~1/3 das músicas,
por **duas** confusões que o histograma de pitch-classes não distingue:

1. **Relativa** (maior ↔ relativa menor): perfis K-S parecidos (Dó maior ≈ Lá
   menor) — detecta a relativa menor onde é a maior.
2. **Paralela** (mesma tônica, modo trocado): songs que oscilam maior/menor
   paralelo (Wave, Chega de Saudade, Valsinha); o Cifra Club ancora num modo, o
   K-S no outro.

Desambiguar com sinais que o histograma ignora: **acorde final, cadência (V→I vs
v→i), primeiro acorde, função do baixo, sensível presente/ausente.** Medir cada
incremento contra o baseline (46% exata / 61% relativa-consciente), **sem quebrar**
a arbitragem modo↔tom existente. Secundário: o K-S não acha a tônica de modos
(`G F C G` → lê Dó maior, não Sol mixolídio).

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
| 1 | Fase B: desambiguar relativa **E** paralela | `tonal-center-detection` | M–L |

_Concluídos: `enharmonic-spelling`, `consolidate-modal-field` (em
`finish-note-spelling`), `widen-key-corpus` (n=28)._

## Contexto de fonte (copyright)

Autoridade: **Almir Chediak, *Harmonia e Improvisação* Vol. I** (`base_estudo/`,
gitignored). Usamos **fatos** (convenções, tonalidades das músicas analisadas) —
nunca o texto, as tabelas-como-diagramadas, nem as cifras das 70 músicas. Os
acordes vêm do Cifra Club; o `scripts/key_baseline.py` guarda só a lista de
músicas + o tom anotado pelo **próprio Cifra Club** (fatos públicos), não as
cifras — corpus independente da Parte 4 do livro.
