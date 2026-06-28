# Roadmap & Handoff

Princípio que guiou tudo: **fundação antes de produto; derivar em vez de
transcrever; medir em vez de achar.** A teoria do Chediak (Vol. I) está
destilada, implementada e testada; a fronteira agora é **precisão** e
**apresentação** para o público BR.

## Regra de ouro — fonte vs. verdade

> **Cifra Club = input bruto.** Mina de acordes (texto); a utilidade **acaba no
> scraping**. As anotações da fonte (tom, maior/menor) são pistas crowdsource, **não a
> verdade** — e **não codificam o centro modal**.
> **Algoritmo + Chediak = ground truth.** Tensão/repouso, centro tonal e nomenclatura
> modal só nascem **depois** do motor processar o dado bruto, ou validados contra a
> literatura. Nunca leia o significado direto da fonte.

Corolário (a lição que re-bloqueou o `modal-center-arbitration`): um alvo só é
implementável se **o dado bruto o codifica**; quando o CC não codifica o fato de Chediak,
a frente fica **bloqueada por dado** — precisa de corpus curado, não de mais mecanismo.

## Status (2026-06-28)

**Feito e no `main`** (~24 changes OpenSpec, 273 testes verdes, `openspec/`
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
- **Fase B v3 — filtro de afinação + recalibração da banda** — `tune-tie-band`: duas
  correções cirúrgicas. (1) `cifra_core/lines.py` passa a descartar linhas de afinação
  ("Afinação Drop D", "Capotraste") que eram parseadas como acordes e poluíam o perfil
  K-S. (2) `TIE_BAND` recalibrado de 0.06 → **0.10**: Papel Marché (João Bosco,
  gold=C) tinha gap K-S ~0.09 — C major ficava fora da banda apesar de corrob=7.00 vs
  0.00 de A minor. **Resolve Papel Marché** (de ERRO → exato).
- **Incremento 1 — segmentação de modulação real** — `modulation-regions`: medição
  honesta + apresentação limpa das músicas bitonais (Chediak p. 116-118, modulação
  por acorde pivô — em Wave/Chega de Saudade o A7 é V7 de Ré menor E de Ré maior). (1)
  Nova `dominant_regions` pós-processa `segment_keys` (window=8 intacto) fundindo
  fragmentos < 10% dos acordes → 2-4 regiões legíveis (Wave: 21 → ~3). `tonal_regions`
  no relatório passa a usá-la. (2) Gold multi-região `(primária, [secundárias])` no
  baseline + `evaluate_modulating_song` (acerto parcial = primária; total = todas as
  regiões). Wave e Chega saem do denominador monotonal e viram **acerto total**
  (Dm + D maior detectados). **Não toca** `detect_key`/`TIE_BAND`/`segment_keys`.

**Baseline de detecção de tonalidade** (`uv run python scripts/key_baseline.py`,
ouro = tom do Cifra Club, com a Fase B v1+v2+v3 + o gate de qualidade do 3b):
- **Monotonais (n=58):** **modo 86% · tônica exata 69% · relativa-consciente 76% ·
  coleção (armadura) 97%**. (Antes do gate de qualidade: 67/74; o gate corrigiu Garota
  de Ipanema — V-como-tônica — sem regredir nada.)
- **Centro estrutural (Chediak, degree-relative, `chediak-structural-gold`):** **79%**
  (15/19 verificados por dominante funcional). O buraco restante = 4 casos de
  V-detectado-como-tônica (A Banda, Aquele Abraço, Apesar de Você, Menino do Rio), onde
  o sinal de **qualidade** não é limpo o bastante para o gate disparar com segurança.
- **Leitura da coleção 97%** (`collection-aware-metric`, Incremento 3a): das falhas de
  tônica-exata, só **2** erram a coleção diatônica de fato (Desafinado +10, Começar de
  Novo +3); as demais acertam a armadura e erram só o **centro** dentro dela. Métrica
  **aditiva** — a tônica-exata segue o número honesto de primeira classe.
- **Modulantes (n=2):** acerto parcial 100% · acerto total 100% (Wave, Chega).

(Progressão: K-S puro 64/46/61 → Fase B v1+v2 83/62/72 → +v3+gate **86/69/76**. Sem gap
de transposição, a tônica-exata é honesta. O gate de qualidade só corrige o centro quando
o palpite do K-S aparece **exclusivamente como dominante-7** e resolve num acorde de
repouso — ultraconservador, zero regressão.)

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

1. ~~**Segmentação das modulações reais**~~ — **feito** em `modulation-regions`
   (`dominant_regions` + gold multi-região; Wave/Chega medidas como modulantes, acerto
   total; window=8 e `detect_key` intactos).
2. ~~**Tunar/afrouxar o EPS da banda**~~ — **feito** em `tune-tie-band` (TIE_BAND
   0.06→0.10; filtro de linhas de afinação; Papel Marché resolvido; modo 83%→87%).
3. **Casos residuais** — *Esquinas*/*Lilás*/*Açaí* (Djavan, harmonia modal complexa),
   e a tônica de modos de igreja pelo K-S (`G F C G` lido como Dó maior).
   - **3a — métrica coleção-consciente** — **feito** em `collection-aware-metric`:
     4ª métrica `same_collection` (a tônica detectada é grau diatônico do gold ≈
     armadura) no harness e no baseline + verdict "coleção" por música. Mede honestamente
     que o resíduo é centro-dentro-da-coleção (97%), não detector quebrado. Não toca
     `detect_key`/`segment_keys`/`TIE_BAND`/`modal.py`.
   - **3b-pré — aposentar o `detect_mode` falso** — **feito** em
     `fix-or-remove-church-mode`: a detecção automática de modo de igreja foi removida do
     pipeline (gerava "Centro modal: X frígio" errado em 12/60 — todos eólios reais,
     zero modo verdadeiro). Provado por sondagem que dois consertos in-place não
     convergem (cadência modal: sintético 8/8→3/8, 6 falsos; só fundamentais: 8/8→2/8,
     10 falsos). A **biblioteca modal** (campo/cadências/tabelas Chediak pp.122-125)
     fica intacta; o campo morto `KeyEstimate.church_mode` saiu. Baseline **idêntico**
     (não toca detecção). Remove a mentira ativa e desbloqueia o 3b.
   - **3b-cor — coloração modal (overlay tonal-ortodoxo)** — **feito** em
     `modal-coloring-overlay`: reintroduz o modalismo como **anotação descritiva** sobre a
     análise tonal — não eixo concorrente. `detect_coloring` resume os empréstimos já
     computados, **ancorado na tônica do `detect_key`** (sem re-centrar), e emite
     `modal_coloring` (campo + linha PT-BR), omitido por padrão. v1 = **mixolídio** (sobre
     maior: bVII→I / bVII / v-menor) e **frígio** (sobre menor: bII→i estrutural ≥2);
     dórico fora (compartilha coleção → depende do 3b). Gatilhos calibrados contra o
     ground-truth de Chediak (pp. 124-127, `scripts/modal_coloring_groundtruth.py`):
     dispara em Ponteio/Upa Neguinho/Canto de Ossanha, **silêncio** nas eólias
     (Wave/Corcovado/Insensatez/Construção). Divergências vs Chediak documentadas
     (arranjo: Procissão tonalizada; centro: Arrastão Ré-maior↔Lá-dórico). Baseline
     **idêntico**. O detector lê harmonia, não melodia.
   - **3b-corpus — 2º ouro + métrica de centro** — **feito** em `chediak-structural-gold`:
     `center_accuracy` invariante a transposição (offset relativo ao tom do Cifra Club),
     sobre o subconjunto **verificado por dominante funcional** (Chediak p.84/87), com
     proveniência (verified/chediak/unverified) blindando contra anotação crowdsource. As 4
     métricas Cifra-Club **idênticas** (86/67/74/97). **Buraco de centro tonal: 74%
     (14/19)** — 5 casos de V-detectado-como-tônica (Garota F→C, A Banda D→A, Aquele Abraço
     E→A, Apesar D→A, Menino do Rio F→C). A validação restringiu o escopo a tonal: o centro
     **modal** (offset≠0) foi adiado porque seu offset não pode vir de subtração absoluta
     (Chediak↔Cifra Club podem divergir de transposição — Pra Não Dizer Mi vs Fá). É o
     pré-requisito (a) do gate.
   - **3b-gate — gate de qualidade (V-como-tônica)** — **feito** em
     `tonal-center-tritone-gate`: o `detect_key` corrige o centro escapando da TIE_BAND
     quando o palpite do K-S aparece **só como dominante-7** e resolve numa 5ª abaixo num
     acorde de **repouso** (Chediak: tônica repousa, V é tensão). Robusto a secundários (o
     sinal é a saúde do repouso da peça, não notas) e a blues (sem repouso → aborta). Duas
     abordagens antes falharam a trava (4-filtros: exata 67→36% por disparar em
     secundários; coleção-fit: 0 alvos + modo −3) — a densidade de secundários da MPB
     derrota discriminadores de coleção/trítono. O de qualidade venceu: exata 67→**69%**,
     relativa 74→**76%**, centro 74→**79%** (Garota corrigida), modo/coleção idênticos,
     **zero regressão**. Conservador: só 1 dos 5 alvos (os outros 4 não têm sinal de
     qualidade limpo). dim7-como-dominante fica para change própria.
   - **3b-gate-v2 — afrouxar o gate de qualidade (V-como-tônica residual)** — **feito** em
     `loosen-tritone-gate`: um SEGUNDO caminho no `_tritone_gate`, ancorado no **alvo de
     resolução** em vez da pureza do V. Caminho A (Y exclusivamente dominante → Garota)
     intacto; caminho B corrige Y→X=(Y−7) mesmo quando Y descansa OCASIONALMENTE, se um
     V7/SubV **funcional** resolve em X (estrutural), X é o repouso **predominante** e X é o
     **primeiro acorde** (a abertura é a âncora robusta; o último engana — Esquinas FECHA na
     relativa, e usá-lo regrediria o modo, flagrado pela trava ao vivo). Hipótese validada por
     sondagem+simulação read-only ANTES de codar. Corrige **A Banda, Apesar de Você, Menino do
     Rio** (V→I): exata **69→74%**, relativa **76→81%**, **centro 79→95% (18/19)**, modo 86% e
     coleção 97% **idênticos**, **zero regressão**. Resta só **Aquele Abraço** (tônica `I7` de
     funk: a tônica real soa como dominante e o IV parece repouso — caso distinto, change própria).
   - **II cadencial secundário/auxiliar** — **feito** em `ii-cadential-secondary-auxiliary`:
     Chediak XIX (p.100, lida do scan). Um acorde **menor** separado do dominante por 4ªJ
     ascendente (ii→V) é um II cadencial; o tipo vem do **alvo do dominante** (5ª abaixo):
     tônica→**primário** (`Dm7 G7`), grau diatônico→**secundário** (`F#m7 B7`→Em = de V7/III),
     empréstimo→**auxiliar** (`Cm7 F7`→Bb = de V7/bVII). Antes o secundário virava `Emp`
     (errado) e o auxiliar `T`; o `D2` ("Segunda Cadencial") estava morto (SD pegava `ii`
     antes) e foi revivido para os 3 tipos. Sem metro nas cifras, usa a relação harmônica (não
     o tempo forte). Camada de função, **baseline idêntico**; 334 testes (+8). Fecha XVIII-XIX.
   - **dominante auxiliar + SubV7 secundário** — **feito** em
     `dominant-auxiliary-and-secondary-subv`: Chediak XVIII (p.99, lida do scan). O **alvo**
     distingue: dominante **secundário** prepara grau diatônico (V7/x), **auxiliar** prepara
     acorde de **empréstimo modal** (`Bb7→Eb` = V7/bIII; novo código `Daux`). O **SubV7
     secundário** prepara grau diatônico resolvendo ½t abaixo (`Ab7→G` = SubV7/V; `Eb7→Dm` =
     SubV7/ii). Reorganizou o ramo de dominante: I7/IV7 blues (XXXIV) → resolução funcional →
     bVII7/bVI7-empréstimo-sem-resolução → secundário/SubV primário (a resolução precede a
     leitura de empréstimo: `Bb7`/`Ab7` que resolvem deixam de ser `Emp`; `Bb7→C` segue Emp).
     Camada de função, **baseline idêntico**; 326 testes (+8). Próxima: II cadencial XIX.
   - **classificação completa do diminuto** — **feito** em `classify-diminished-chords`: o
     diminuto não-dominante deixa de ser rotulado **"Empréstimo Modal"** (errado: empréstimo é
     tríade/tétrade maior/menor de modo paralelo, nunca um diminuto) e passa a ser classificado
     por TIPO (Chediak XXI-XXII, pp.102-104): **descendente** (fundamental desce ½t),
     **auxiliar** (bordadura: sai e volta ao mesmo acorde), e genérico de passagem. O
     **ascendente** segue dominante (`dim7-as-dominant`) e o `vii°7` segue D. Limpou o ramo
     `"Dim"` que virou código morto (ofuscado pelo `0c`). Camada de função, **baseline
     idêntico**; 318 testes (+6). Sondagem ao vivo flagrou o buraco (descendente/auxiliar→`Emp`).
   - **dim7-como-dominante (V7(b9) rootless)** — **feito** em `dim7-as-dominant`: um
     diminuto de 7ª é um V7(b9) **sem fundamental** (Chediak p. 90, "diminutos equivalentes
     e relação com V7(9-)"): `B°7` = `G7(b9)` − G → dominante de C. Na **camada de função**
     (não no parsing): um dim7 que resolve um semitom acima da raiz escrita vira dominante —
     primário (`°7 = V7(b9)` de I) ou secundário rootless (`°7 = V7(b9)/x`); sem essa
     resolução é diminuto de aproximação (sem função dominante). Ganha escala diminuta
     (octatônica do dominante implícito, raiz−4) e numeral de grau alterado (`#i°7`/`#iv°7`),
     **preservando** a marca `°7`. Decisão de risco: **não** toca `Category`/parsing nem
     `_tritone_gate`/`detect_key` → baseline **idêntico** (modo 86 · exata 69 · relativa 76 ·
     coleção 97 · centro 79), zero regressão; +9 testes (309 verdes). v2 (adiada): resolução
     descendente, alvo estável, baixo do alvo (slash).
   - **3b-modal — arbitragem modal de centro** — **BLOQUEADO POR DADO** (proposta
     `modal-center-arbitration` aberta, NÃO implementada). A sondagem ao vivo dos 4 fatos
     `chediak` (a trava do baseline, rodada ANTES de qualquer código) invalidou a premissa do
     design — o centro modal de Chediak **não está codificado nas cifras do Cifra Club**:
     - **Arrastão** (Chediak Lá dórico; cc_key=**G**, não Ré): `_central_pc` dá **Mi** (baixo
       Mi×11, Lá×8, Ré×8), a peça **termina em `D7+`**, e Lá só empata em 2º. Não há cadência
       a Lá — o finalis Lá é **inrecuperável** por qualquer heurística harmônica.
     - **Procissão** (Chediak Dó mixolídio; cc_key=Ré): Dó aparece **1×** em 80 acordes — a
       peça oscila Ré/Lá. Centro Dó **impossível** a partir destas cifras.
     - **Upa Neguinho** (Chediak Ré mixolídio) e **Pra Não Dizer** (Chediak Mi eólio): o
       **centro já é detectado certo** (Ré maior / Fá menor = finalis); só o **nome do modo**
       diverge (mixo/eólio vs maior/menor) — trabalho de `modal_coloring`, não recuperação de
       centro. Seus cc_key ainda estão transpostos vs. as cifras (Upa B, Pra Não Dizer Fá).

     Conclusão (regra de ouro acima): a arbitragem está **bloqueada por dado, não por
     mecanismo** — exige um **corpus de MPB modal curado** cujas cifras codifiquem o finalis
     (melodia indisponível; harmonia-só não basta). Construir o overlay+métrica como
     especificado embarcaria um detector que erra Arrastão e uma métrica ~0% nos únicos casos
     de divergência real — ou forçaria fudge do gold (proibido). A métrica degree-relative
     ([[center-eval-degree-relative]]) e o overlay ficam de pé como design; reabrir quando o
     corpus existir. A **coloração** modal (3b-cor) já entrega o *sabor* hoje.
   - **3b — arbitragem modal↔tonal de centro** — **bloqueado**: a falha de centro espalha
     por V/vi/iii/IV sem gate único, e cada gate arriscaria as ~41 corretas. A detecção de
     **centro** modal (separar Lá dórico de Ré mixolídio em Arrastão; tonalizar o silêncio
     da coloração) é uma change futura: exige (a) um **corpus de MPB modal curado** e (b)
     um **discriminador modal↔tonal principiado** — o critério do Chediak que separa
     mediante de mixolídio (resolução de dominante funcional, pp. 121-123) sobre acordes
     reais. A coloração (3b-cor) entrega o **sabor** modal hoje; o **centro** fica para cá.

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
| ~~1~~ | ~~Segmentar modulação real (Wave/Chega) na apresentação~~ | ~~`modulation-regions`~~ | ~~M~~ |
| ~~2~~ | ~~Afrouxar/tunar o EPS da banda (agora com n=60)~~ | ~~`tune-tie-band`~~ | ~~S~~ |
| ~~3a~~ | ~~Métrica coleção-consciente (armadura)~~ | ~~`collection-aware-metric`~~ | ~~S~~ |
| ~~3b-pré~~ | ~~Aposentar o `detect_mode` falso (preserva biblioteca)~~ | ~~`fix-or-remove-church-mode`~~ | ~~S~~ |
| ~~3b-cor~~ | ~~Coloração modal (overlay tonal-ortodoxo: mixolídio/frígio)~~ | ~~`modal-coloring-overlay`~~ | ~~M~~ |
| 3b | Arbitragem modal↔tonal de **centro** (corpus modal + discriminador) | — (bloqueado) | L |

_Concluídos: `enharmonic-spelling`, `consolidate-modal-field` (em
`finish-note-spelling`), `widen-key-corpus` + leva 2 (n=60), `tonal-center-detection`
(Fase B v1, relativa), `parallel-mode-correction` (Fase B v2, paralela; modo
64%→83% acumulado), `tune-tie-band` (Fase B v3, filtro de afinação + TIE_BAND
0.06→0.10, Papel Marché resolvido; modo 83%→87% acumulado), `modulation-regions`
(Incremento 1, `dominant_regions` + gold multi-região; Wave/Chega como modulantes),
`collection-aware-metric` (Incremento 3a, 4ª métrica coleção/armadura 97%; mede o
resíduo como centro-dentro-da-coleção, não detector quebrado), `fix-or-remove-church-mode`
(3b-pré, remove a detecção automática de modo falsa — 12/60 frígios espúrios — preservando
a biblioteca modal; baseline idêntico), `modal-coloring-overlay` (3b-cor, reintrodução
tonal-ortodoxa do modalismo como overlay descritivo ancorado: mixolídio/frígio, calibrado
contra Chediak pp.124-127; dispara em Ponteio/Canto de Ossanha, silêncio nas eólias)._

## Contexto de fonte (copyright)

Autoridade: **Almir Chediak, *Harmonia e Improvisação* Vol. I** (`base_estudo/`,
gitignored). Usamos **fatos** (convenções, tonalidades das músicas analisadas) —
nunca o texto, as tabelas-como-diagramadas, nem as cifras das 70 músicas. Os
acordes vêm do Cifra Club; o `scripts/key_baseline.py` guarda só a lista de
músicas + o tom anotado pelo **próprio Cifra Club** (fatos públicos), não as
cifras — corpus independente da Parte 4 do livro.
