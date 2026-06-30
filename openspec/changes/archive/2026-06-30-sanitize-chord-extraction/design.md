## Context

Hoje a extração de acordes tem três peças e falta uma quarta. `clean_cifra_lines`
(`lines.py`) remove ruído estrutural mas **preserva** linhas de letra (por contrato, para
manter ordem e display). `ChordPattern.CHORD` (`chords.py`) casa o símbolo completo, mas a
pilha de qualidades é `*` (zero-ou-mais) e o baixo é opcional, então uma letra `A–G`
isolada casa. `_extract_chords` (`analysis_service.py:81-88`) roda `find_all` em **toda**
linha e concatena. Não existe um classificador que diga "esta linha é cifra ou letra" — e
é exatamente esse o sinal de desambiguação. Medição ao vivo: 14% dos tokens (429/3015) são
letra-única; 277 linhas de prosa injetam 409 fantasmas; em 21/62 músicas o último acorde
(candidato a tônica no `chediak_functional_center`) é uma palavra.

O corpus local (`cifras/*.md`) já traz um manifesto `Acordes Utilizados:` por música — um
vocabulário confiável que podemos usar como confirmação de tokens ambíguos.

## Goals / Non-Goals

**Goals:**
- Eliminar os tokens-fantasma de letra na fonte (extração), sem re-curar os `.md`.
- Manter `clean_cifra_lines` idempotente e a ordem/preservação das linhas (display intacto).
- Zero regressão do invariante funcional (62/62) — medido ao vivo no baseline.
- Whitelist OPCIONAL: o classificador por densidade sozinho já resolve a maioria; a
  whitelist é precisão extra quando a fonte declara vocabulário.

**Non-Goals:**
- IR tipado `ParsedCifra` (Fase 2). Aqui a classificação é uma função de leitura, não um
  novo modelo de dados.
- ChordPro / conversão duas-linhas→ChordPro (Fase 3).
- Mexer em `detect_key`, gates funcionais, `modal_coloring` — intocados.

## Decisions

**D1 — Classificador por densidade em `cifra_core.lines`, não no consumidor.**
`classify_line(line, *, threshold=0.6) -> LineKind` (enum CHORD/LYRIC/SECTION). Razão =
`#tokens-que-parseiam-como-acorde / #tokens-não-vazios`. Tokens de barra/decoração (`/`,
`|`) são ignorados do denominador. Fica em `cifra_core` porque é a "fonte única" de
conhecimento de cifra (mesmo princípio do `clean_cifra_lines`); scraper e analyzer
consomem a mesma função. *Alternativa rejeitada:* apertar só o regex para não casar letra
isolada — frágil, quebra cifras legítimas com tríade pelada (`A`, `D`, `E`) e não barra
prosa como "Feio não é bonito" cujo `F` é real-formato mas falso-contexto.

**D2 — "Acorde válido" do classificador = FULLMATCH do token inteiro, não `parse`.**
Para medir densidade, um token conta como acorde se o regex canônico casa o token
**inteiro** (`re.fullmatch`), não só um prefixo. Crucial: `parse("Brasil")` NÃO falha (casa
a raiz `B` e ignora `"rasil"`), então "parse aceita" contaria prosa como acorde — o furo.
`fullmatch` rejeita `Brasil`/`Com`/`Desse`/`Feio` (o resto não é gramática de acorde) e
aceita `C`/`Am7`/`G/B`. Mantém a regra "um regex de acorde só". `find_all` (não-ancorado)
está descartado pelo mesmo motivo. Token `Em` (palavra "em") dá fullmatch como Mi-menor,
mas numa linha de prosa a densidade total continua baixa ⇒ LYRIC: a *linha* resolve, não o
token.

**D3 — Whitelist injetada como parâmetro opcional, fluindo do ingest ao extrator.**
`cifra_from_text(text, *, known_chords: frozenset[str] | None = None, ...)` e o
`_extract_chords(lines, *, known_chords=None)`. A regra do token ambíguo: um símbolo que
parseia como **tríade maior de raiz nua** (`A–G`, sem qualidade, sem baixo) só é admitido se
`known_chords is None and classify==CHORD` **ou** `symbol in known_chords`. Símbolos
não-ambíguos (têm qualidade/extensão/baixo) passam direto. *Alternativa rejeitada:*
embutir a whitelist no modelo `Cifra` — acopla dado de fonte ao contrato tipado; um
parâmetro mantém `Cifra` puro (Fase 2 decide o modelo).

**D4 — Os scripts de baseline parseiam o manifesto e passam a whitelist.**
Um helper local nos scripts extrai os símbolos do header `Acordes Utilizados:` (já está em
backticks) e passa como `known_chords`. O parser do manifesto NÃO entra no `cifra_core`
(é específico do formato `.md` do corpus); fica nos scripts. Generalização para a lista de
acordes do Cifra Club é Fase 2+.

## Risks / Trade-offs

- **[Limiar 0,6 corta uma linha de cifra esparsa real]** (ex.: uma linha com 1 acorde e
  3 palavras de anotação) → Mitigação: o limiar é parâmetro; medir no baseline; linhas de
  cifra reais do corpus são densas (`C / / G / Am`), prosa é esparsa em acordes válidos.
  Gate quantitativo: invariante 62/62 + queda dos fantasmas confirmam calibração.
- **[Tríade pelada legítima sem whitelist e em linha mista]** → Mitigação: sem whitelist,
  cai na classificação de linha; se a linha for densa em acordes, a tríade passa. O caso
  patológico (tríade pelada sozinha numa linha de prosa) é raro e aceitável perder.
- **[Mudança de contrato no consumidor]** `_extract_chords` passa a depender da
  classificação → Mitigação: assinatura retrocompatível (`known_chords` default `None`),
  e o caminho sem classificação some (uma fonte só de extração, como manda o spec).
- **[Quebra de testes existentes que assumem extração linha-a-linha]** → Mitigação:
  rodar `make test`; ajustar fixtures que dependiam do comportamento antigo, documentando.

## Migration Plan

1. Implementar `classify_line` + enum em `cifra_core.lines` com testes unitários (cifra
   densa, prosa PT-BR, marcador de seção, linha de barra).
2. Adicionar a regra do token ambíguo + parâmetro `known_chords` na extração
   (`chords.py`/consumidor), mantendo símbolos não-ambíguos intactos.
3. Fiar `cifra_from_text` e `_extract_chords` para propagar a whitelist e ler só linhas
   CHORD.
4. Adicionar parse do manifesto nos dois scripts; passar `known_chords`.
5. **Gate ao vivo:** rodar `scripts/songbook_baseline.py` antes/depois; invariante 62/62,
   fantasmas ≈0, último-acorde dos 21 casos deixa de ser palavra. `make test`/`make lint`.
6. Rollback trivial: a whitelist é opcional e a classificação é aditiva; reverter o
   commit restaura o comportamento anterior sem migração de dados.

## Open Questions

- Limiar exato (0,6 é palpite calibrável) — decidir empiricamente no passo 5.
- SECTION vs LYRIC para linhas como `Introdução: Dm7 G7` (rótulo + acordes na mesma linha):
  tratar o prefixo `Palavra:` como descartável e classificar o resto por densidade.
