# AGENTS.md

> Fonte canônica de fatos do projeto para qualquer ferramenta de AI
> (Claude Code, Antigravity, Gemini CLI). Cada ferramenta lê isto por um caminho
> próprio — ver "Pontes por ferramenta" no fim.

Análise harmônica automática de MPB: a partir de cifras do Cifra Club, extrai
acordes, tonalidade, graus, funções, cadências e progressões, e gera relatórios
(JSON/Markdown/HTML). Monorepo `uv` com núcleo compartilhado + CLI + scraper.

## Regra inegociável — Chediak é o árbitro teórico

Toda decisão harmônica deve ser checada contra **Almir Chediak, _Harmonia &
Improvisação_ Vol. I** (a autoridade do projeto): **cite a página**, registre
divergências, **nunca chute**. Quando a teoria for ambígua, o livro decide. Modelo
interno em inglês canônico (`Note` soletrada, bemóis corretos — `Bb`, não `A#`);
relatórios humanos em PT-BR.

## Regra de ouro — separação de responsabilidades (fonte vs. verdade)

- **Cifra Club = input bruto (texto).** É a mina de acordes (sequências de
  caracteres). Sua utilidade **termina no scraping**. As anotações da fonte (o "tom",
  o rótulo maior/menor) são pistas crowdsource-ingênuas, **não a verdade** — confundem
  relativa/paralela, transpõem por tessitura, e **não codificam o centro modal** (provado
  ao vivo: em Arrastão o centro de Chediak é Lá, mas as cifras do CC não têm finalis em Lá).
- **Seu algoritmo + Chediak = ground truth.** O *significado* dos acordes — tensão/repouso,
  centro tonal, nomenclatura modal — só nasce **depois** que o motor (parsers, filtros,
  gates de qualidade) processa o dado bruto, ou quando validado contra a literatura
  (Chediak / academia). Nunca leia o significado direto da anotação da fonte.

Corolário operacional: um alvo de detecção/centro só é implementável se **o dado bruto
o codifica**. Quando o corpus do CC não codifica o fato de Chediak (centro modal), a frente
fica **bloqueada por dado** — precisa de um corpus curado, não de mais mecanismo.

## Layout (monorepo `uv` workspace)

```
packages/
├── cifra_core/         # núcleo: encoding, filtro de linhas (idempotente),
│                       #   regex de acorde, Cifra/SongRef, SongProvider, cache
├── cifra_scraper/      # API Flask (BeautifulSoup) em :3000/api — serviço opcional
└── harmonic_analysis/  # domínio musical + CLI `harmonic` + relatórios
```

A análise obtém cifras de fontes **navegáveis** (catálogo) pela porta `SongProvider`:
dois adaptadores — **in-process** (padrão, raspa sem subir servidor) e **HTTP** (fala com
o Flask). Cache via `CachePolicy` (`NETWORK_FIRST`/`CACHE_FIRST`/`CACHE_ONLY`/`REFRESH`).
O Cifra Club é **um adaptador de entrada substituível, não o núcleo**: há também uma
ingestão **local** `cifra_core.cifra_from_text` (texto/`.txt` → `Cifra`, `key=""`) que cai
no MESMO motor (`analyze_song_data_structured`), via `harmonic analyze-file`, sem rede.
Note que o motor **já detecta a tonalidade só dos acordes** (`detect_key`) — o `Tom:` do
CC nunca é muleta de detecção (é só metadado de relatório + ouro de validação). Entrada
local é metadata-free e não entra no baseline (sem ouro do CC).

## Comandos

```bash
uv sync                                  # instala todo o workspace
uv run harmonic analyze "Djavan" "Sina"  # CLI (in-process, sem servidor)
uv run harmonic analyze-file prog.txt    # analisa um .txt de acordes local (sem rede)
make test                                # uv run pytest (toda a suíte)
make lint                                # uv run ruff check packages
uv run python scripts/songbook_baseline.py  # baseline funcional (Chediak, corpus local cifras/)
make scraper                             # sobe o Flask em :3000 (só p/ --provider http)
```

- Python ≥ 3.12, `ruff` line-length 88, `pytest` testpaths = `packages`.
- Testes ficam em `packages/<pkg>/tests`; layout `src/` em cada pacote.

## Fluxo de trabalho — OpenSpec (obrigatório p/ mudanças não-triviais)

Cada melhoria é uma **change OpenSpec**: proposal → design → specs → tasks →
implementar → `openspec archive`. O OpenSpec é a **espinha agnóstica de
ferramenta**: a verdade vive em `openspec/specs/` (capabilities) e
`openspec/changes/` (arquivadas em `openspec/changes/archive/AAAA-MM-DD-<nome>/`).

```bash
openspec list           # changes ativas
openspec list --specs   # capabilities (specs)
```

## Convenções

- **Git:** branch dedicada para mudanças grandes — `feature/<slug>` ou `fix/<slug>`.
- **Uma fonte de nota** (`Note` soletrada) e **uma detecção de tom** (`detect_key`)
  em todos os entry points — não reintroduzir subsistemas paralelos.
- Seções de análise degradam **visíveis** (`_safe_section` + `result["diagnostics"]`),
  nunca em silêncio.

## Estado atual

Teoria destilada/implementada/testada (46 changes arquivadas + `fix-d2-over-attribution` e
`fix-cadence-function-coherence` prontas p/ arquivar, **429 testes verdes**).

**Coerência cadência×função fechada (`fix-cadence-function-coherence`, fecha o #6):** o detector
de cadência classificava a família autêntica/plagal por GRAU, ignorando a FUNÇÃO do alvo — rotulava
`V→I` como cadência mesmo quando o coder chamava o "I" de `D2`/`Dim` (5 músicas). Chediak define a
cadência pela **combinação D→T** (XXXII p.110); um dominante resolvendo num acorde que é ele mesmo um
ii é **resolução direta** (XXXIII p.111), não cadência. Agora `analyze_cadences` recebe os
`function_code`s e **suprime** (não reclassifica como deceptiva) a família autêntica/plagal quando o
alvo é função não-repouso (começa com `D`/`Sub`). O `songbook_baseline.py` ganhou o **4º gate** —
coerência cadência×função, robusto à ambiguidade de string (par só é defeito se TODAS as ocorrências
são tensão) — **VERDE 62/62** sobre **175 cadências reais** validadas (dentes: pega as 5 incoerências
no comportamento pré-fix). **#6 fechado** (trítono · diminuto · D2 · cadência, todos 62/62).

**`D2` (ii cadencial) deixou de ser super-atribuído (`fix-d2-over-attribution`):** o ramo 0e
emitia `D2` pela QUALIDADE do próximo acorde (é dominante-7?), sem checar se ele FUNCIONA como
dominante. Agora um pré-passe `ii_cadential_indices` (molde do `subv_extended_indices`, intervalar,
transposição-invariante) só valida o `D2` se o dominante **resolver no seu alvo** (o acorde em
`i+2` baixa em `(Vroot+5)%12`) — teste que NÃO depende do tom nem do código (evita a armadilha do
blues-pos, que coda I7/IV7 como T/SD antes da resolução). **Resultado:** `D2` 363→**199** (164
over-attributions zerados, 199 legítimos mantidos, incl. `Em7 A7→D7` secundário); invariantes
trítono/diminuto **62/62**. O invariante "todo `D2` resolve no alvo" **agora é gate** no
`songbook_baseline.py` (`_d2_resolution_invariant`, re-deriva a resolução intervalar sobre a SAÍDA,
independente do pré-passe) — nasce **VERDE 62/62** sobre **199 D2 reais** validados; fecha a parte
ii-V do #6.

**Gate de regressão funcional crescido (`grow-functional-invariants`, frente #6 parcial):** o
`songbook_baseline.py` agora gateia **DOIS** invariantes duros, ambos transposição-invariantes e
**62/62**: (a) trítono real ⇒ função dominante; (b) **diminuto (XXI-XXII / p.90) nunca é
Emp/SD/T/Modal** — só `D`/`Dsec` (vii°7 rootless) ou `Dim`. Um probe (n=62) mostrou que as outras
duas famílias do #6 NÃO estavam verdes e viraram **fixes** primeiro, **gates** depois: `fix-d2-over-
attribution` (~168 incoerências `D2`→não-dominante — o `D2` casava pela QUALIDADE do próximo acorde,
não pela FUNÇÃO) e `fix-cadence-function-coherence` (5 Perfeitas com cadência×função discordando).
**Ambos hoje são gates verdes** (`_d2_resolution_invariant`, `_cadence_coherence_invariant`).
Princípio: um gate nasce VERDE; invariante já violado é relatório de bug, não gate.

**Endurecimento do achador funcional (`harden-functional-center`, frente #7 parcial):** a
adjudicação da worklist limpa mostrou que metade das divergências eram erros do PRÓPRIO
`chediak_functional_center`, violando "tônica repousa, V é tensão". Duas guardas Chediak-puras
(pp.84-85) no achador: o alvo da resolução só estabelece tônica se for de **repouso**
(não-dominante, `not is_dom`) **e** com **raiz==baixo** (rejeita inversão `Fm/C` como tônica).
**Resultado:** invariante **62/62** mantido; concordância de centro **80%→83% (48/58)**; worklist
12→10. Casos: velhos-tempos/ate-parece passam a concordar, a-ra vira quarentena honesta, ciume
deixa de ser falsa-concordância (chamava o dominante `E7(9)` final de tônica). A guarda é precisa:
inutil-paisagem/razao-de-viver permanecem porque têm resolução a repouso real (`E7→A7M`).

**Higienização de extração (Fase 1, `sanitize-chord-extraction`):** a extração de acordes era
lossy — o regex casava letra maiúscula `A–G` isolada como acorde e o pipeline rodava em TODA
linha, então palavras de letra viravam fantasmas (`Brasil`→`B`, "E"→`E`): 14% dos tokens
(429/3015) eram letra-única, 277 linhas de prosa injetavam tokens. Fix em `cifra_core`:
`classify_line` (densidade de acordes válidos por `re.fullmatch`, não `parse` — `parse("Brasil")`
casa `B`) decide CHORD/LYRIC/SECTION; `extract_chords_from_lines` lê **só** linhas CHORD e
confirma token ambíguo (raiz nua) contra uma whitelist opcional (vinda do header `Acordes
Utilizados:` dos `.md`). **Resultado medido:** fantasmas 14%→**0,5%**; invariante **62/62 mantido**;
concordância de centro **71%→80% (47/59)**; cobertura 58→59. `cifra_from_text` segue puro (a
whitelist é preocupação de extração, não de ingestão). Fases 2/3 (IR tipado `ParsedCifra`;
ChordPro) seguem abertas.

**Fundação de validação (reformulada em `songbook-chediak-baseline`):** o **Cifra Club é só
fonte de cifra — base de nada**. O **Chediak é a base de validação** (regras funcionais
rigorosas) e o **songbook** (`cifras/*.md`, local/gitignored) é o corpus baseline. As 4 métricas
ancoradas no `cc_key` (modo/exata/relativa/coleção) e o tier de centro ancorado no `cc_key` foram
**aposentados**. O baseline roda em `scripts/songbook_baseline.py` (corpus local via
`cifra_from_text`, sem scraping) e mede:
- **Invariante funcional** (a base rochosa, transposição-invariante): todo trítono real ⇒
  dominante. Atual: **62/62 sem defeito**.
- **Centro tonal por CORROBORAÇÃO** (não acurácia): `detect_key` × `chediak_functional_center`
  (acha a tônica pela resolução do dominante funcional, pp.84/87, sem anotação). Cobertura
  **58/62** (4 em quarentena modal/estática); **concordam 48/58 (83%)** = centros de alta
  confiança (41/58 → 47/59 após `sanitize-chord-extraction` limpar fantasmas → 48/58 após
  `harden-functional-center` endurecer as guardas de repouso); as divergências viram **worklist
  de curadoria** (o Chediak adjudica), nunca placar do detector. **Princípio:** a tonalidade absoluta é só quadro de exibição — a análise funcional
  é invariante a transposição; tudo nasce da música + Chediak, nada do CC.

A **bifurcação analítica (A)+(B) está completa**: (A) nomeia o modo que o algoritmo detecta
("D mixolídio"); (B) anota o centro modal que a cifra não codifica mas Chediak documenta
(Arrastão → Lá dórico p.125; Procissão → Dó mixolídio p.126), via corpus curado n=2.

A Fase B (centro tonal) está madura: desempate cadencial (v1, confusão relativa), correção
de modo paralelo (v2), filtro de afinação (v3), e o **gate de qualidade do 3b** — corrige
o V detectado como tônica quando o palpite do K-S aparece só como dominante-7 e resolve num
acorde de repouso (Chediak: tônica repousa, V é tensão; densidade de secundários da MPB
derrota discriminadores estatísticos — só o funcional vence). O modalismo virou **overlay
descritivo** (`modal-coloring`), não eixo concorrente; a detecção de modo automática falsa
foi removida.

**Já fechados (camada de função + detecção):** `dim7-as-dominant` (viio7 = V7(b9) rootless,
Chediak p.90), `loosen-tritone-gate` (V-como-tônica residual: exata 69→74, centro 79→95),
`i7-funk-anchor-gate` (Aquele Abraço = tônica `I7` de funk: K-S pega o IV, âncora first==last
corrige p/ a tônica — centro 95→**100% (19/19)**, exata 74→76), `classify-diminished-chords` (diminuto
descendente/auxiliar deixam de ser `Emp`, Chediak pp.102-104), `modal-mode-naming` (parte
**(A)** da bifurcação analítica: promove o `modal_coloring.flavor` a nome de modo no display
— "D mixolídio"/"D frígio" ao lado da leitura tonal; pura apresentação, baseline idêntico).
`modal-center-arbitration` (parte **(B)**, **fechada via Caminho 2 = anotar, não detectar**):
corpus tipado `harmonic_analysis.corpus.modal_centers` (citação obrigatória — `__post_init__`
+ teste-invariante = gate), nota do curador no display (MD blockquote + HTML `alert`/`<cite>` +
JSON com citação estruturada), e **ledger de cobertura/divergência** (não acurácia: nada é
detectado), transposição-seguro pelo intervalo curado `finalis_from_tonal`. O *bloqueio por
dado* da detecção (Caminho 1) continua válido e está documentado em PROBE-FINDINGS.md.

Também fechados: `dominant-auxiliary-and-secondary-subv` (Chediak XVIII p.99 — dominante
auxiliar = alvo de empréstimo modal; SubV7 secundário; código `Daux`),
`ii-cadential-secondary-auxiliary` (Chediak XIX p.100 — II cadencial primário/secundário/
auxiliar pelo alvo do dominante; revive o `D2`), `extended-dominants` (Chediak XXVIII(a)
pp.107-108 — dominante que resolve em OUTRO dominante por 4ªJ = `Dext`, sem número romano,
escala mixolídio; gate após o blues) e `extended-subv` (Chediak XXVIII c/d — SubV estendido por
semitom, com **detecção de cadeia** via pré-passe `subv_extended_indices`: runs maximais ≥3,
só a cadeia conta — o par local é ambíguo com blues; corrige o gap `Dext`→`"D"` no macro do
HMM). A preparação de graus (XVIII-XIX) e os dominantes/SubV estendidos (XXVIII a/c/d) estão
completos.

**Frentes abertas (handoff pós-2026-06-30 — ver ROADMAP "Sequência sugerida" + nota de Handoff):**
- ✅ **Gateado o invariante "todo `D2` resolve no alvo"** no `songbook_baseline.py`
  (`_d2_resolution_invariant`) — VERDE 62/62 sobre 199 D2 reais; parte ii-V do #6 fechada. *(feito)*
- ✅ **`fix-cadence-function-coherence` — #6 FECHADO.** `analyze_cadences` consulta a função do alvo
  e suprime a família autêntica/plagal quando o "I" funciona como tensão (`D`/`Sub`); 4º gate de
  coerência no baseline (VERDE 62/62, 175 cadências reais). *(feito)*
- **#7 Worklist de corroboração**: ~10 divergências genuínas restantes (caiu de 17) — agora erros
  prováveis do `detect_key` (V/relativa-como-tônica, mistura modal). Adjudicar com Chediak — **sem**
  reamarrar no CC. Usar `scripts/worklist_adjudication.py` (READ-ONLY).
- **#8 Ampliar o corpus** (`cifras/*.md`): o ouro é a regra, não o gênero.
- **Legado**: acordes interpolados (XXIX, refinaria de rótulo, risco/ganho ruim); detecção de
  centro modal (Caminho 1, bloqueado por dado).

**Regra de ouro:** o Cifra Club é só fonte de cifra; o Chediak é a base. Toda mudança no motor
mede contra o **baseline funcional ao vivo** (`songbook_baseline.py`) — não contra anotação do CC.
A análise funcional é invariante a transposição; nunca reintroduzir o `cc_key` como ouro.

---

## Pontes por ferramenta (como cada uma lê este arquivo)

- **Claude Code** → `CLAUDE.md` faz `@AGENTS.md` (import nativo).
- **Antigravity** → `.agent/rules/project.md` (`trigger: always_on`) repete as leis
  e aponta para cá; o Antigravity não lê AGENTS.md direto.
- **Gemini CLI** → `~/.gemini/settings.json` com `context.fileName` incluindo
  `AGENTS.md`.
