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

**Camada de persistência (`persist-analysis-corpus`, frente #8):** a saída do motor deixou de ser
efêmera — `harmonic_analysis/persistence/` disseca o `result` num banco **DuckDB** (11 tabelas,
grão = ocorrência de acorde) via `harmonic corpus build` (roda o motor sobre `cifras/*.md`, sem
rede). O banco é **view materializada** do motor (derivado, regenerável por `engine_version`/
`git_sha`; snapshot por `analysis_run`), **nunca ouro** competindo com Chediak (sem `cc_key`-
verdade; centro é ledger `agree/diverge/quarantine`). Gates viram **views SQL** (`v_gate_*`) +
`harmonic corpus gates`. **Achado ao materializar:** os gates de **trítono e diminuto do
`songbook_baseline.py` são no-ops** — chamam `Chord.get_category()`/`Chord.bass` (inexistentes)
dentro de `try/except: continue`, então o "170/170 verde" desses dois é **vacuoso**. Rodando a
checagem correta: diminuto=0 (vira gate executável real), mas **trítono=944 flags em 155/170**
(dominado por `→T` de I7 blues/funk e `→Emp` modal — exceções que o próprio projeto legitimou).
Logo trítono virou **ledger de curadoria** (`v_ledger_tritone_nondominant`, informativo, NÃO
bloqueia); o bug do baseline + adjudicação Chediak das exceções são a change separada
**`fix-baseline-noop-gates`**.

**Bug do baseline corrigido (`fix-baseline-noop-gates`):** os acessores fantasma
(`Chord.get_category()`/`.bass`) trocados pelos que existem (`.quality`/`.properties.bass`) —
os gates **executam de fato**. Resultado real: **diminuto/D2/cadência 170/170 verdes** (gates
duros reais), e o **trítono é ledger afiado = 519** ocorrências em 124/170 (a classe limpa
**I7-como-tônica** — função `T` no grau `I`/`i`, blues/funk, `i7-funk-anchor` — foi **isentada**:
425 das 944; a mesma isenção afia `v_ledger_tritone_nondominant`). Os ~519 restantes (`→T` em
VI/III = T-por-grau, `→Emp` backdoor, `→Outro`) são **worklist honesta**, adjudicação Chediak
página-a-página fora do escopo (não se cita o que não se tem). O trítono **não é gate verde** — é
ledger; o "170/170" agora só vale para os três invariantes limpos.

**Perda silenciosa de linhas coladas corrigida (`fix-glued-chord-density`):** a auditoria de
completude (2026-07-02) achou que token de acorde colado em barra de ritmo (`Am6/`, `Bm7/`) não
contava na densidade do `classify_line` (não é fullmatch nem malformado — resíduo vazio), a linha
virava LYRIC e era descartada INTEIRA sem diagnóstico: 11 músicas, 20 linhas, ~109 acordes
perdidos (dindi 26→52 acordes, samba-em-preludio 25→52). Fix: `_glued_chord_token` (cláusula (d)
do malformado invertida) conta na densidade — classificação e extração concordam; decoração pura
(`///`) saiu do denominador. **Efeito medido:** 3 gates duros seguem **170/170**; corroboração de
centro **123→125/153 (82%)** (a perda alimentava a worklist); ledger de trítono 519→**532** (+13
recuperados a adjudicar).

**Quarentena de completude (`corpus-completeness-quarantine`):** as cifras incompletas da
auditoria viraram **ledger curado** (`harmonic_analysis/corpus/completeness.py`, padrão
`modal_centers`: evidência obrigatória, falha-rápido, só fatos — zero texto de cifra):
**15 `incomplete`** (oráculo forte — o header `Acordes:` do songbook v4 declara acordes ausentes
do corpo; truncamento PDF→MD, irrecuperável sem a fonte; piores: a-paz, no-cordao-da-saideira,
tempo-feliz) + **13 `suspect`** (manifesto independente divergente, pós-desconto de dialeto por
pitch-classes). `song.completeness` é estampado no `corpus build`; o `report` mostra a contagem e
marca a worklist de trítono (ocorrências de cifra parcial pesam menos na adjudicação). **Gates
duros NÃO filtram** (invariante por ocorrência vale em cifra parcial). Anti-drift:
`scripts/audit_completeness.py` re-deriva a evidência com a extração corrente e acusa divergência
com o ledger (hoje: SEM drift). O **v3 é ponto cego declarado** (fonte deletada, manifesto
derivado do corpo — sem oráculo, sem quarentena gratuita).

**Quarentena v4 RESOLVIDA pela fonte (`retranscribe-v4-quarantined`):** os 5 volumes do
Songbook Bossa Nova chegaram em `songbooks/` (PDF, **gitignored** — copyright; offset do Vol.4:
PDF = página do livro − 20). As 15 `incomplete` foram **re-transcritas do livro** (tom impresso,
verificação mecânica extração ⊇ diagramas 15/15) — a corrupção era pior que truncamento: páginas
perdidas (se-todos perdeu a p.133), codas descartadas (a-paz), **transposição espúria**
(tempo-feliz estava em Sol; o livro imprime Ré) e OCR mangling (Eb7M≈Ebm7, Em7≈Em6, B7M4≈B6(9)).
As 15 saíram do ledger com proveniência; as seções do md-fonte local foram reparadas
(header+fence). **Efeito medido:** gates duros **170/170** (a teoria generaliza no dado
corrigido), corroboração de centro **125→127/153 (83%)**, completude `incomplete=0`/`suspect=13`.
**Risco registrado:** as outras ~36 do v4 podem ter corrupção que o oráculo de vocabulário não
detecta (auditoria ampla v4×livro = candidata a change). **Fato corrigido (2026-07-05):** o
**Vol. 1 (62 músicas) JÁ É o corpus original n=62** (conferido contra o índice; "Vols. 1/2/5
nunca ingeridos" era erro — só valia p/ 2 e 5). A proveniência do Vol.1 é a conversão antiga
(mesma família lossy do v4 → risco na auditoria ampla). O **Vol. 2 foi ingerido em 2026-07-05**
(ver frente #8); o **Vol. 5 (65) segue pendente**.

**Ledger de trítono ADJUDICADO (`TRITONE-ADJUDICATION.md`, 2026-07-02):** os 532 casos foram
adjudicados contra **Chediak XXXIV pp.111-116** (o PDF do Vol. I está em `base_estudo/`), pela
GEOMETRIA real (raiz vs. tônica + resolução), não pelo rótulo. Vereditos: **bVI7 `Emp` legítimo**
(63, Subd. menor alterada, quadro p.113); **bVII7 condicional** (157: `→I` = AEM backdoor
legítimo p.112(1); `→bIII` = V7/bIII, dominante — codar `Emp` é defeito, p.114); **`T` em
VI7/III7/bIII7 = BUG T-por-grau** (177: são V7/II, V7/VI etc. resolvidos/deceptivos, `Dsec`
p.114(1) — trítono real nunca é T por posição, exceção I7 blues p.112(3), agora citável);
**`Outro` em VII7/II7 classificável** (73: VII7 "Cadencial" p.112(2), II7 "Subd. alterada"
p.113(4), com guarda de resolução no I). Residual honesto pós-follow-ups: ~60-90 ambíguos.
Follow-ups: `fix-tritone-t-by-degree` (✅) e `classify-special-function-dominants` (✅) —
**adjudicação COMPLETA**: ledger final = **20 ocorrências em 10/170** (só bV7→Emp genérico,
ambíguo honesto). O **cap. XXXIV do Chediak está integralmente implementado e citado no coder**:
funções especiais (I7/IV7 blues, bVII7/bVI7 Emp, II7 SD alterada, VII7 cadencial/V7-III),
secundários deceptivos (0f), e resolução-precede-empréstimo (bVII7→4ªJ diatônica = Dsec).

**T-por-grau eliminado (`fix-tritone-t-by-degree`, follow-up 1 da adjudicação):** novo ramo
**0f** no coder — dominante-7 que atravessa a cascata aplicada sem casar, com raiz em
VI/III/bIII, vira **`Dsec` deceptivo** com alvo esperado `(V7/x)` (Chediak XXXIV(b)(1),
p.114); trítono real nunca mais recebe `T` por posição (exceção única: I7 blues p.112(3)).
Escopo cirúrgico: II7/VII7 (função especial p.115(4)) e o fall-through restante ficam para a
change seguinte. **Efeito medido:** ledger **532→318** (−214), 3 gates duros seguem
**170/170**, corroboração de centro inalterada (125/153). Restam no ledger: bVII7 (86),
bVI7 (31), VII7 (40), II7 (33), Emp/? (126) — insumo da `classify-special-function-dominants`.

**Analytics de corpus (`corpus-analytics`):** 5 views musicológicas descritivas sobre o banco
(`v_cadence_distribution`, `v_function_trigram`, `v_vocab_by_mode`, `v_secondary_density`,
`v_tritone_ledger_patterns`) + `harmonic corpus report` → relatório Markdown PT-BR (6 seções,
denominadores visíveis, **nunca placar** — guarda-corpo testado). A view de padrões agrupa o
ledger de trítono por (função×grau×qualidade): os 519 casos soltos viram padrões adjudicáveis —
insumo direto da futura adjudicação Chediak.

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

**Notação não-identificada é reportada, não descartada (`report-unidentified-notations`):** um
token em posição de acorde que não parseia (ex.: `D9/S`, baixo `/S` inválido — 61× no corpus) era
**perdido em silêncio** por dois caminhos: (1) tankava a densidade da linha → LYRIC → a linha sumia
inteira; (2) `find_all` chutava o prefixo (`D9`) e jogava o resto fora. Agora
`malformed_chord_token` (híbrido: prefixo de acorde válido + resto começando com `/`/`(` + resíduo
com lixo após remover TODOS os acordes+decoração) detecta o malformado; a densidade o **conta** (a
linha não some, recupera os válidos), a extração **coleta** o token em `unidentified` sem **chutar**
o prefixo, e o motor injeta em `result["diagnostics"]` (degradação VISÍVEL, escolha do usuário:
coleta, não exceção). Poupa letra (`Brasil`→resto `rasil`, fora do escopo) e acordes colados
(`Gm7(11)///Gb7(#11)///`→resíduo vazio). Medido n=119: **0 regressão** (só os `X9` chutados de
`X9/S` somem, agora reportados; upa-neguinho 5→25 acordes válidos), 4 gates **119/119**.

**Fundação de validação (reformulada em `songbook-chediak-baseline`):** o **Cifra Club é só
fonte de cifra — base de nada**. O **Chediak é a base de validação** (regras funcionais
rigorosas) e o **songbook** (`cifras/*.md`, local/gitignored) é o corpus baseline. As 4 métricas
ancoradas no `cc_key` (modo/exata/relativa/coleção) e o tier de centro ancorado no `cc_key` foram
**aposentados**. O baseline roda em `scripts/songbook_baseline.py` (corpus local via
`cifra_from_text`, sem scraping) e mede:
- **Invariantes funcionais** (a base rochosa, transposição-invariantes): **três gates duros
  verdes 170/170** — diminuto (XXI-XXII), D2-resolução (XIX) e cadência×função (XXXII). O quarto,
  "trítono real ⇒ dominante", **não é invariante limpo** (tem exceções legítimas: I7-tônica de
  blues/funk) — vira **ledger de curadoria** (519 ocorrências pós-isenção I7; ver
  `fix-baseline-noop-gates`), não gate. Nota histórica: os gates de trítono/diminuto eram no-ops
  (acessor fantasma) — o antigo "170/170 do trítono" era vacuoso; hoje diminuto executa verde e
  trítono é ledger honesto.
- **Centro tonal por CORROBORAÇÃO** (não acurácia): `detect_key` × `chediak_functional_center`
  (acha a tônica pela resolução do dominante funcional, pp.84/87, sem anotação). Cobertura
  **153/170** (17 em quarentena modal/estática); **concordam 125/153 (82%)** = centros de alta
  confiança (41/58 → 47/59 após `sanitize-chord-extraction` → 48/58 após `harden-functional-center` → 123→125/153 após `fix-glued-chord-density` recuperar linhas coladas; histórico: 48/58 após
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
derrota discriminadores estatísticos — só o funcional vence). O gate ganhou um **3º caminho
(`add-cadential-v-as-tonic-path`, Path C)**: corrige o V-como-tônica quando o `V→I` está na
ABERTURA (fora da janela final que o Path B varre), com guardas Chediak — ≥2 resoluções V→X, X=1º
acorde, e a peça NÃO fecha em Y como repouso (desempata "abre no IV mas fecha na tônica"). Aditivo
(A/B intactos); fecha `a-volta`/`dia-de-vitoria` da worklist (concordância 121→123), zero regressão.
O modalismo virou **overlay
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
- ✅ **#7 Worklist ADJUDICADA (n=170)** (2026-07-01, `WORKLIST-ADJUDICATION.md`): as **32**
  divergências viram fatos musicológicos citados. Achado: sem vencedor único — funcional-certo (14:
  V/IV/ii/iii/relativa-como-tônica), detect-certo (9: v/ii/pivô tonicizado no fim), **NOVO — armadilha
  do ii-V (3: `bolinha-de-sabao`/`menina`/`rio` — vamp ii-V, detect pega o V, funcional pega o ii,
  nenhum pega o I)**, e 6 modulantes. **Não há regra-cega segura** → worklist é curadoria, não placar.
  Gate futuro do `detect_key` teria de ser cirúrgico (V/ii-como-tônica alta-conf com V→I limpo a
  repouso), sem tocar os detect-certo; a armadilha ii-V pede o achador preferir o ALVO do V (o I) ao ii.
- 🔄 **#8 Ampliar o corpus** (`cifras/*.md`): **62→119→170→231** (songbooks Bossa Nova v3 +57,
  v4 +51 via `scripts/split_songbook.py`; **Vol. 2 +60 em 2026-07-05** via `ingest-songbook-vols-2-5`).
  Nota histórica de método: v3/v4 vieram de conversão automática PDF→MD (origem da corrupção do v4);
  o **Vol. 2 foi transcrito à mão página-a-página do PDF** (`songbooks/`, offset PDF=livro−25),
  só-acordes, com **admissão verificada** (`scripts/verify_transcription.py`: extração⊇diagramas) —
  nenhuma música entra sem `ok`. Fontes gitignored (copyright). **Gates duros seguem 231/231**
  (diminuto/D2/cadência; a teoria generaliza sem defeito); centro 170/207 (82%); ledger trítono 32;
  496 testes verdes. Fatos da ingestão do Vol.2 (ordem NÃO-alfabética; 2 fantasmas do índice-irmão —
  `se-e-tarde-me-perdoa`, "Eu sei que…" — que não existem no volume; header do livro = autoridade de
  compositor) em `openspec/changes/ingest-songbook-vols-2-5/INGESTION-DECISIONS.md`. Nota de dado: v3
  tinha `X9/S` (61x, baixo inválido) — hoje **reportado** em `diagnostics` (ver
  `report-unidentified-notations`). **Falta o Vol. 5 (65 músicas)**; o ouro é a regra, não o gênero.
- **Legado**: acordes interpolados (XXIX, refinaria de rótulo, risco/ganho ruim); detecção de
  centro modal (Caminho 1, bloqueado por dado). **`grow-modal-center-corpus` arquivada-como-parked
  (2026-07-01)** — data-gated em n=2 (Vol. I §XXXVI.4 exaurido); crescer o corpus modal precisa de
  NOVA autoridade citada (Chediak Vol. II/academia), não de mais mecanismo. Arquivada com
  `--skip-specs` (nada entregue). Reabrir/nova change quando surgir a fonte.

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
