# Roadmap & Handoff

Princípio que guiou tudo: **fundação antes de produto; derivar em vez de
transcrever; medir em vez de achar.** A teoria do Chediak (Vol. I) está
destilada, implementada e testada; a fronteira agora é **precisão** e
**apresentação** para o público BR.

## Status (2026-06-26)

**Feito e no `main`** (~18 changes OpenSpec, ~248 testes verdes, `openspec/`
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

**Baseline de detecção de tonalidade** (`uv run python scripts/key_baseline.py`,
vs ouro Chediak, n=6): **modo 67% · tônica exata 33% · relativa-consciente 67%**.
A exata é deprimida por **transposição** (versão do Cifra Club ≠ tom do Chediak);
o problema *real e sistemático* é a **confusão maior ↔ relativa menor**.

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

Alvo **afiado pelo baseline**: a fraqueza sistemática é a **confusão maior ↔
relativa menor** (os perfis Krumhansl-Schmuckler de maior e relativa menor são
parecidos). Desambiguar com sinais que o histograma de pitch-classes ignora:
**acorde final, cadência (V→I vs v→i), primeiro acorde, função do baixo.**
Medir o ganho contra o baseline. Secundário: o K-S não acha a tônica de modos
(`G F C G` → ele lê Dó maior, não Sol mixolídio).

## Trilha paralela (contida, encaixa a qualquer momento)

- **Spelling enarmônico** — `describe_modal_borrowing`/`transpose` ainda
  colapsam em sustenido (`A#` onde é `Bb`); rotear pela `Note` soletrada. É a
  Tensão #2 da exploração inicial, ainda aberta. (`enharmonic-spelling`)
- **Consolidação legada** — `MODE_HARMONY` ainda coexiste com o `modal_field`
  derivado; aposentar o `normalize_note` sustenido-só. (`consolidate-modal-field`)
- **Ampliar o corpus de validação** — mais músicas com ouro Chediak (fatos) em
  `scripts/key_baseline.py`; cuidado com a transposição (a métrica de modo é
  invariante).

## Sequência sugerida (próximas sessões)

| # | Tema | Change | Tam. |
|---|---|---|---|
| 1 | Fase B: desambiguar relativa maior/menor | `tonal-center-detection` | M–L |
| 2 | Spelling enarmônico | `enharmonic-spelling` | S–M |
| 3 | Consolidação legada | `consolidate-modal-field` | S |

## Contexto de fonte (copyright)

Autoridade: **Almir Chediak, *Harmonia e Improvisação* Vol. I** (`base_estudo/`,
gitignored). Usamos **fatos** (convenções, tonalidades das músicas analisadas) —
nunca o texto, as tabelas-como-diagramadas, nem as cifras das 70 músicas. Os
acordes vêm do Cifra Club; o `scripts/key_baseline.py` guarda só a lista de
músicas + tons do Chediak (fatos), não as cifras.
