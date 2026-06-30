# Tasks — sanitize-chord-extraction

> Fase 1 da higienização de extração: classificador de linha por densidade (decide a
> linha) + whitelist de vocabulário (confirma o token). Escopo `cifra_core` + um ajuste no
> consumidor `_extract_chords`. Gate ao vivo no `scripts/songbook_baseline.py`.

## 1. Trava de baseline (referência antes de mexer)

- [x] 1.1 Rodar `uv run python scripts/songbook_baseline.py` e registrar a referência:
      invariante (esperado 62/62), cobertura/concordância de centro, e a contagem atual de
      tokens-fantasma de uma letra (script auxiliar do diagnóstico). Anotar no PR/handoff.

## 2. Classificador de linha por densidade (`cifra_core.lines`)

- [x] 2.1 Adicionar `LineKind` (enum CHORD/LYRIC/SECTION) e
      `classify_line(line, *, threshold=0.6) -> LineKind`. "Acorde válido" = `re.fullmatch`
      do regex canônico contra o token INTEIRO (D2), NÃO `parse`-aceita (que ignora lixo:
      `parse("Brasil")` casa `B`). Tokens de barra/decoração (`/`, `|`) fora do
      denominador. Prefixo `Palavra:` (ex.: `Introdução:`) é descartado antes de medir
      densidade (D1/Open Q).
- [x] 2.2 Testes unitários: cifra densa (`C / / G / Am` → CHORD), prosa PT-BR
      (`Com seu passado E tradição` → LYRIC), linha `É livre e é feliz E tem tudo...` →
      LYRIC, marcador → SECTION, `Introdução: Dm7 G7` → CHORD (após tirar o rótulo).
- [x] 2.3 Confirmar que `clean_cifra_lines` segue idempotente e preservando as linhas
      (a classificação é leitura pura, não remove nem reordena).

## 3. Confirmação de token ambíguo por whitelist (extração)

- [x] 3.1 Implementar a regra do token ambíguo (D3): um símbolo que parseia como **tríade
      maior de raiz nua** (`A–G`, sem qualidade, sem baixo) só é admitido se
      `(known_chords is None and linha==CHORD)` **ou** `symbol in known_chords`. Símbolos
      não-ambíguos (com qualidade/extensão/baixo) passam direto, sem depender da whitelist.
- [x] 3.2 Testes: `Brasil`/`Com`/`Desse` numa linha de prosa não produzem `B`/`C`/`D`;
      `A` numa linha de cifra (com whitelist contendo `A`) é extraído; sem whitelist, `A`
      só sai de linha CHORD.

## 4. Fiação ingest → extrator

- [x] 4.1 **Refinado na implementação:** a whitelist é preocupação de EXTRAÇÃO, não de
      ingestão — `cifra_from_text` só normaliza linhas e não extrai, então NÃO recebe
      `known_chords` (parâmetro seria morto e acoplaria dado de fonte ao ingest). A
      whitelist entra no momento da extração: via `data["known_chords"]` em
      `analyze_song_data_structured` e via `extract_chords_from_lines(..., known_chords=)`
      direto nos scripts. `Cifra` segue puro (decisão D3 preservada).
- [x] 4.2 `_extract_chords` (analysis_service): ler **só** linhas classificadas CHORD e
      aplicar a whitelist aos tokens ambíguos. Remover o caminho que escaneia toda linha
      (uma fonte só de extração, como manda o spec). Manter assinatura retrocompatível.
- [x] 4.3 Testes do consumidor: cifra mista (acordes + letra) → sequência de acordes só de
      linhas CHORD; linhas LYRIC/SECTION contribuem zero tokens.

## 5. Manifesto → whitelist nos scripts (corpus local)

- [x] 5.1 Helper local (nos scripts, NÃO em `cifra_core`) que extrai os símbolos do header
      `Acordes Utilizados:` (já em backticks) de cada `.md`.
- [x] 5.2 `scripts/songbook_baseline.py` e `scripts/worklist_adjudication.py`: parsear o
      manifesto e passar `known_chords` ao `cifra_from_text`/extração.

## 6. Gate ao vivo + zero-regressão + docs

- [x] 6.1 Re-rodar `uv run python scripts/songbook_baseline.py`: **invariante continua
      62/62**; tokens-fantasma de uma letra ≈ 0; as 277 linhas de prosa não contribuem
      tokens; o último-acorde dos 21 casos deixa de ser palavra; cobertura/concordância de
      centro igual ou melhor. Diff contra a referência da task 1.1.
- [x] 6.2 `make test` verde, `make lint` limpo.
- [x] 6.3 Atualizar `AGENTS.md`/`ROADMAP.md`: registrar a Fase 1 da higienização
      (classificador + whitelist), o ganho medido, e que Fases 2/3 (IR tipado, ChordPro)
      seguem abertas. `openspec validate sanitize-chord-extraction --strict` passa.
