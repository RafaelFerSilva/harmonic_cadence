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

## NORTE ATUAL (2026-07-05) — Ingestão ENCERRADA; foco em desenvolvimento & análise (n=293)

**Decisão de escopo (o corpus congela em n=293, Vols. 1–5).** A frente de **aquisição de
dados** (songbooks) está **ENCERRADA**. O que não deu para capturar é **descartado** — não
perseguimos mais a fonte:
- `isaura` (gap de digitalização no PDF do Vol. 5, pp.90–91 ausentes) — **descartada**.
- `se-e-tarde-me-perdoa`, `bate-boca`, `bonita` — **fantasmas de índice-irmão**, não existem
  nos volumes; **descartados** (registro honesto fica no archive da change).
- **Auditoria ampla Vol.1/Vol.4 × livro** (~36+ músicas com possível transposição espúria da
  conversão automática) — **descartada**: não vamos abrir página-a-página atrás disso. Se uma
  análise específica tropeçar num arquivo suspeito, corrige-se pontualmente, não em varredura.
- Novos volumes / corpus modal curado — **fora de escopo** até surgir necessidade *e* fonte
  citável nova (o `modal-center` segue parked por dado, não por mecanismo).

Daqui em diante a régua muda: **desenvolver e analisar o que já temos**, não crescer o dado.

**O que temos (base sólida):** motor neuro-simbólico com a teoria do Chediak Vol. I destilada,
implementada e testada (Cap. XXXIV integralmente citado no coder). Corpus **n=293** (Vols. 1–5)
materializado em **`corpus.duckdb`** (11 tabelas, grão = ocorrência de acorde; `run_id=5`).
**3 gates duros 293/293 verdes** (diminuto XXI-XXII · D2 XIX · cadência×função XXXII) em duas
medições independentes (baseline funcional ao vivo + gates SQL). Centro por corroboração
216/262 (82%); quarentena 31; ledger de trítono 43. `audit_completeness` sem drift. 5 views
musicológicas descritivas + `harmonic corpus report`. PDF do Chediak Vol. I em `base_estudo/`
(página do PDF = página do livro) — citação é viável.

**Próximos passos — duas trilhas (o norte das próximas sessões):**

*Trilha A — ANÁLISE (adjudicação com Chediak; ZERO dado novo, tudo já no repo):*
1. ✅ **Ledger de trítono (43) — ADJUDICADO POR HUMANO 100% (2026-07-07).** Curador × Vol. I
   pp.111-116: **6 `chromatic_approach`** cravadas (**Chediak XXXIV c, p.116**; citação afiada de
   p.111); **bVI7** e **#11** refutadas na leitura → ambiguous honestos; **resíduo bV7** (25)
   confirmado indecidível (consistente com `TRITONE-ADJUDICATION.md`). Flag: `disa/30` possível Dext
   mis-codado → fix downstream. **Final: 6 decididas + 37 ambiguous, nenhuma forçada** (refutar >
   inflar). Infra abaixo (a change `adjudicate-tritone-ledger`):
   🔶 **Ledger de trítono (43) — INFRAESTRUTURA + DRAFT (`adjudicate-tritone-ledger`).** A
   malha neuro-simbólica FECHOU: corpus tipado `corpus.tritone_adjudications` (veredito citado, a
   `Citation` é gate; enum `subv`/`chromatic_approach`/`emp_legitimate`/`dsec_deceptive`/`ambiguous`),
   auditoria anti-drift (`scripts/audit_tritone_adjudication.py`), cruzamento na
   `v_ledger_tritone_nondominant` (+`verdict`/`chediak_page`) e no `corpus report`. **É ANOTAÇÃO
   (PRATA): não muta `function_code`** — fix do coder = change downstream. Draft conservador
   (geometria re-derivada do DuckDB): **6 `chromatic_approach`** (dom-7 um semitom abaixo do dominante
   real, cita p.111) + **37 `ambiguous`** com nota geométrica (bV7 deg=6 / centro instável — o resíduo
   honesto declarado). Correção da própria hipótese: os `#11` (samba/beatriz/ausência) NÃO resolvem
   como SubV. Gates 293/293, coder intocado, +tests. **Falta: revisão do curador (Chediak) para
   promover ambíguos→decisivos com página; depois arquivar.**
2. ✅ **Worklist de centro (46 diverge) — ADJUDICADA (`adjudicate-center-worklist`).** Mesmo padrão
   do trítono: corpus tipado `corpus.tonal_center_adjudications` (`TonalCenterVerdict` = centro
   adjudicado + `winner` + evidência + `Citation` pp.84-85/87), view `v_center_worklist`, §7 do report,
   anti-drift `scripts/audit_center_adjudication.py`. ANOTAÇÃO PRATA — **não toca `detect_key`**.
   Vereditos: **`functional` 28, `detect` 8, `neither_ii_v` 3 (armadilha ii-V), `modulating` 4,
   `ambiguous` 3**. Achado #7 preservado (sem vencedor único). Gates 293/293, detecção intocada, suíte
   727 verde. **Follow-up downstream FEITO (parcial):** `add-ii-v-bracket-center-path` — **Path D
   (bracket ii-V)** no gate do `detect_key`: corrige `bolinha`/`menina`/`rio` → Dó/Dó/Fá quando o
   detect pega o **V de X** e o funcional pega o **ii de X** (os dois cercam a tônica). Único path
   que consulta o achador funcional (o #7 provou ao vivo que todo gate estrutural regride: "abre em
   ii-V" quebra agree/detect-certos). **Zero regressão** (simulação 293 + baseline). Corrige o
   detector, **não** move o placar (216/262: o funcional segue no ii → os 3 seguem `diverge`).
   **Follow-up INVESTIGADO E REJEITADO (2026-07-07, motor intacto):** corrigir o achador funcional a
   preferir o alvo do ii-V ao ii (p/ os 3 virarem agree, 216→219) foi **simulado ao vivo nas 293 e
   dá SALDO NEGATIVO** — a heurística "cand é um ii" quebra **5 agree** de alta confiança (`amazonas`
   Am→Gm, `ate-parece` Em→Ré, `demais` Am→Sol, `e-nada-mais` Am→Gm, `gaiolas-abertas` Ebm→Dó#: são
   tônicas menores legítimas, não ii) para ganhar 3. O #7 vale também para o achador funcional: sem
   regra-cega segura. O único discriminador ("o detect também aponta X") acoplaria `functional_center
   →detect_key` = **recursão** (o Path D já faz o inverso). **Decisão: não mexer no achador** — os 3
   traps seguem `diverge` (os métodos genuinamente discordam), o detect já está correto (Path D) e a
   adjudicação de centro cita o I. Placar 216/262 é **real**, não inflado.

*Trilha B — DESENVOLVIMENTO (evoluir o produto sobre o corpus que temos):*
3. **Camada C — overlay ML/NLP.** As análises do motor são **PRATA** (rótulos derivados de regra +
   Chediak): usar o DuckDB (293 músicas, grão de ocorrência) como dataset para um overlay
   estatístico que **complementa** (não substitui) o símbolo. O símbolo continua dominante; o ML é
   subordinado e corrigível.
   - ✅ **1ª change — `function-anomaly-worklist` (feita):** LM de sequência funcional (backoff
     Witten-Bell) sobre os `function_code`s → **surpresa** por ocorrência → view `v_anomaly_worklist`
     + `harmonic corpus anomalies`. Em vez do alvo circular "prever função e medir contra o coder",
     o produto é uma **worklist de discordância ranqueada** (discordância = SINAL, não erro), cruzada
     com o ledger de trítono (43) e centro-diverge (46): a **Trilha B ordena o que a Trilha A
     adjudica**. Gates duros 293/293 intactos, `function_code` nunca reescrito (PRATA), +14 testes.
   - ✅ **2ª change — `enrich-anomaly-bilateral-degree` (feita):** surpresa **bilateral** (média
     causal+reversa, `BidirectionalModel`) e **bi-canal** (função + grau, `NULL`→`∅`); combinado =
     média dos canais, com componentes visíveis. Pega o que o causal-só-função perdia (resolução
     atípica à direita; função comum em grau raro). Gates 293/293, coder intocado (PRATA), +5 testes.
   - ✅ **3ª change — `harmonic-similarity-retrieval` (feita):** embedding harmônico por música do
     DuckDB (reusa o `Fingerprint` de `style_fingerprint`, **transposição-invariante**), top-K
     vizinhos materializados (`song_neighbor`/`v_song_neighbor`) e `harmonic corpus similar --song
     <slug>` com traços compartilhados. Descritivo (similaridade ≠ qualidade). Gates 293/293, +8 testes.
   - ✅ **4ª change — `harmonic-corpus-clustering` (feita):** famílias harmônicas + medoid por família
     (aglomerativo average-linkage puro-Python sobre os embeddings de estilo, eixo global), materializa
     `song_cluster`/`v_song_cluster` e `harmonic corpus clusters [--k N]`. Descritivo (k do usuário, sem
     "k ótimo"). Achado (k=8): núcleo T-SD-D de 247/293 + satélites distintivos (família `Emp`, família
     `Dsec`) = candidatos à curadoria. Gates 293/293, +7 testes.
   - ✅ **5ª change — `cluster-contrast-traits` (feita):** os traços de família passam de absolutos
     (todos mostravam T,SD,D) para por CONTRASTE (lift vs. média do corpus) — revela o dialeto real
     (Fam Emp+0.15, Fam Dsec+0.096, Fam Deceptiva+3.08); núcleo de 247 sinalizado como baseline.
     Gates 293/293, +2 testes.
   - ✅ **6ª change — `cluster-linkage-option` (feita):** `corpus clusters --linkage {average,complete}`.
     Complete quebra o núcleo-247 numa partição equilibrada (k=8: `[75,71,44,34,31,18,15,5]` vs.
     average `[247,22,8,...]`). average default (compatível). Gates 293/293, +4 testes.
   - Próximas (abertas): peso função×grau / ordenação por componente no overlay de anomalia;
     embeddings aprendidos (song2vec); Ward-linkage; `--metric` (JSD já no domínio); ponderação por
     completude; cutoff de lift/suporte no contraste.
4. **Aprofundar o analytics musicológico** — o retorno de ter 293 músicas: novas views/relatórios
   descritivos (distribuições de cadência, trigramas de função, vocabulário por modo já existem;
   expandir), sempre **denominador visível, nunca placar**. Insumo direto p/ a adjudicação (A).

*Refino de teoria (quando houver apetite, não urgente):* acordes interpolados (Chediak XXIX —
refinaria de rótulo, risco/ganho historicamente ruim). **Parked por dado:** detecção de centro
modal (Caminho 1) — só reabre com NOVA autoridade citada (Chediak Vol. II / academia).

**Invariante de método (não muda):** toda mudança no motor mede contra o `songbook_baseline.py`
ao vivo; pausa-e-investiga se um gate quebrar; adjudicar pela geometria com página citada; o
Cifra Club é só fonte, o Chediak é a base; análise funcional é invariante a transposição.

---

## Status (2026-07-05) — Vols. 2 E 5 do Songbook ingeridos

**`ingest-songbook-vols-2-5` (apply): Vols. 2 e 5 COMPLETOS.** Varredura sequencial página-a-página
dos PDFs (`songbooks/`, offset PDF=livro−25), à mão, só-acordes (anti-filtro), normalização de
empilhado. Vol. 2 = **60/60 reais** (livro pp.26–143); Vol. 5 = **62 transcritas** + 1 gap de scan
(livro pp.31–160). **Corpus 170→231→293.** Cada cifra passou o **gate de admissão**
`scripts/verify_transcription.py` (extração⊇diagramas): nenhuma entra sem `ok`.

**Métricas ao vivo (n=293):** 3 gates duros **293/293** (diminuto/D2/cadência — a teoria generaliza
sem defeito no dado ampliado) · corroboração de centro **216/262 (82%)**, quarentena 31 · ledger de
trítono **43** em 20 músicas · `audit_completeness` (n=293) **SEM drift**.

**Fatos da ingestão** (`.../ingest-songbook-vols-2-5/INGESTION-DECISIONS.md`): ordem do livro **NÃO
é alfabética**; **header da página = autoridade de compositor**; **fantasmas de índice-irmão** —
Vol.2: `se-e-tarde-me-perdoa`, "Eu sei que…"; Vol.5: `bate-boca`, `bonita` (nenhum consta no índice
do próprio volume). **Achado Vol.5:** o índice próprio (PDF p.3) declara **63 músicas**; `isaura`
(livro p.90) é **REAL mas caiu num gap de digitalização** — as pp.90–91 faltam no PDF (offset salta
−25→−27, = as 2 páginas), irrecuperável sem re-scan. O verificador força correções sem fabricar
(`omit3`→forma sem-omit; `rosa-morena` D#° de passagem recuperado do diagrama+partitura).

**Próximo:** `corpus build`/`gates`/`report` DuckDB final (tarefa 4.2, adiada) e arquivar a change.
Oportunístico: re-scan da fonte p/ recuperar `isaura`; auditoria ampla Vol.1/Vol.4×livro.
Nada commitado ainda nesta rodada (arquivos-ouro e PDFs gitignored — só fatos entram).

## Status (2026-07-02) — HANDOFF DA SESSÃO "corpus & adjudicação"

**8 changes arquivadas num dia (56 no total), 496 testes verdes, tudo na `main`
(`1279d99..cc34fe1`).** A sessão transformou a saída do motor num corpus persistido, honesto e
curado contra a fonte física. Detalhe canônico de cada change no AGENTS.md ("Estado atual");
aqui, o mapa:

1. **`persist-analysis-corpus`** — banco DuckDB (11 tabelas, grão = ocorrência de acorde,
   snapshot por `analysis_run`), CLI `harmonic corpus build|gates|report`. Banco = view
   materializada do motor, NUNCA ouro.
2. **`fix-baseline-noop-gates`** — descoberto que os gates de trítono/diminuto do baseline eram
   **no-ops** (acessor fantasma): "170/170" vacuoso. Corrigido: 3 gates duros REAIS
   (diminuto/D2/cadência); trítono virou ledger com isenção I7 citável.
3. **`corpus-analytics`** — 5 views musicológicas + relatório MD PT-BR (nunca placar).
4. **`fix-glued-chord-density`** — token colado (`Am6/`) derrubava linhas inteiras da extração
   sem diagnóstico (dindi 26→52 acordes). Views escopadas ao run corrente (bônus).
5. **`corpus-completeness-quarantine`** — ledger curado de completude (evidência obrigatória,
   padrão modal_centers) + `scripts/audit_completeness.py` (anti-drift) + `song.completeness`.
6. **`fix-tritone-t-by-degree`** + 7. **`classify-special-function-dominants`** — a adjudicação
   **`TRITONE-ADJUDICATION.md`** executada: o **PDF do Chediak Vol. I está em `base_estudo/`**
   (página do PDF = página do livro; dá para LER e citar). Cap. XXXIV integralmente
   implementado no coder. **Trajetória do ledger de trítono: 944 (vacuoso) → 519 → 532 → 318
   → 21** (bV7→Emp genérico, ambíguo honesto, parked).
8. **`retranscribe-v4-quarantined`** — os **5 volumes do Songbook Bossa Nova estão em
   `songbooks/`** (PDF, gitignored; offset Vol.4: PDF = página − 20). As 15 cifras
   `incomplete` foram **re-transcritas do livro** (verificação mecânica 15/15); a corrupção da
   conversão original incluía páginas perdidas, codas descartadas e **transposição espúria**
   (tempo-feliz estava em Sol, o livro imprime Ré). Quarentena v4 resolvida
   (`incomplete=0`, restam 13 `suspect` das originais).

**Métricas ao vivo (n=170, run 4 do banco):** 3 gates duros **170/170** · corroboração de
centro **127/153 (83%)**, quarentena 17 · ledger de trítono **21** em 11 músicas · completude
`complete=157 / suspect=13 / incomplete=0` · auditoria de completude **SEM drift**.

**Próximos passos (ordem recomendada):**
1. **#8 Corpus DuckDB + arquivar** — **Vols. 1–5 ingeridos** (n=293; Vol. 2 +60 e Vol. 5 +62 em
   2026-07-05, à mão página-a-página, admissão por `verify_transcription.py`). Falta rodar o
   `harmonic corpus build`/`gates`/`report` DuckDB final (tarefa 4.2, adiada por ser cara) e
   **arquivar a change**. Oportunístico: re-scan da fonte p/ recuperar `isaura` (gap de digitalização
   no PDF do Vol. 5); `se-e-tarde-me-perdoa` segue fantasma sem volume de origem.
2. **Auditoria ampla v4×livro** (~36 músicas restantes) — a transposição espúria só é
   detectável abrindo a página (o oráculo de vocabulário não a vê quando o vocabulário fecha).
3. **Adjudicar as 13 `suspect`** das originais (oráculo fraco) e o **bV7 (21)** quando houver
   página que decida.
4. **Camada C — ML/NLP overlay** sobre o banco (anomalia→worklist, similaridade, LM de
   progressões) — dados agora limpos; ML nunca arbitra (as 170 análises são PRATA, circular
   p/ treino supervisionado). Abrir com `/openspec-explore` próprio.

**Método (inegociável, provado 8× hoje):** OpenSpec propose→apply→archive; medir SEMPRE
contra `songbook_baseline.py` ao vivo (política pausa-e-investiga: gate quebrado = investigar,
nunca forçar verde); probe READ-ONLY antes de codar; adjudicar pela GEOMETRIA (raiz vs. tônica
+ resolução medida), nunca pelo rótulo; fatos citados com página; commit+push na main ao
arquivar. Copyright: `songbooks/`, `cifras/`, `*.duckdb`, `corpus-report.md`, md-fontes —
tudo gitignored; só FATOS entram no repo.

---

## Status (2026-06-28) — histórico

**Feito e no `main`** (36 changes OpenSpec arquivadas, 334 testes verdes, `openspec/`
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

**Baseline FUNCIONAL** (reformulado em `songbook-chediak-baseline`):
`uv run python scripts/songbook_baseline.py`. O **Cifra Club é só fonte de cifra** (base de
nada); o **Chediak é a base de validação**; o **songbook** (`cifras/*.md`, local) é o corpus.
As 4 métricas ancoradas no `cc_key` foram **aposentadas**. Mede agora:
- **Invariantes funcionais** (transposição-invariantes): **três gates duros verdes** — diminuto,
  D2-resolução, cadência×função (**170/170**). O "trítono ⇒ dominante" **não** é gate: tem
  exceções legítimas (I7-tônica de blues/funk) e virou **ledger** de 519 pós-isenção I7
  (`fix-baseline-noop-gates` corrigiu os gates no-op de acessor fantasma).
- **Centro por CORROBORAÇÃO** (`detect_key` × centro funcional do Chediak, sem anotação):
  cobertura **58/62**, concordam **41/58 (71%)**; divergências = worklist de curadoria.

_(Histórico aposentado, ouro = tom do Cifra Club: modo 86 · exata 76 · relativa 83 · coleção
97 · centro verificado 19/19. Media fidelidade ao CC, não à teoria — por isso saiu.)_

- **Centro estrutural (Chediak, degree-relative, `chediak-structural-gold`):** **100%**
  (19/19 verificados por dominante funcional). O `i7-funk-anchor-gate` fechou **Aquele
  Abraço** (tônica `I7` de funk) — **nenhum buraco de centro restante**.
- **Leitura da coleção 97%** (`collection-aware-metric`, Incremento 3a): das falhas de
  tônica-exata, só **2** erram a coleção diatônica de fato (Desafinado +10, Começar de
  Novo +3); as demais acertam a armadura e erram só o **centro** dentro dela. Métrica
  **aditiva** — a tônica-exata segue o número honesto de primeira classe.
- **Modulantes (n=2):** acerto parcial 100% · acerto total 100% (Wave, Chega).

(Progressão: K-S puro 64/46/61 → Fase B v1+v2 83/62/72 → +v3+gate 86/69/76 →
+loosen-gate **86/74/81**. Sem gap de transposição, a tônica-exata é honesta. O gate de qualidade só corrige o centro quando
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
   - **gate de âncora I7-funk (XXXIV)** — **feito** em `i7-funk-anchor-gate`: fecha o último
     buraco de centro (**18/19→19/19**), Aquele Abraço (Gilberto Gil), tônica funk **I7** em
     Mi lida como Lá. Geometria **inversa** ao gate de trítono: a tônica real é o **V** do
     palpite K-S (o K-S pega o **IV**, mais frequente e que descansa, no vamp I7-IV7); corrige
     `Y→X=(Y+7)` (sobe 5ª) por um sinal **estrutural** (abre E fecha em X), não funcional —
     não há V→I a Mi. Cinco guardas ultraconservadoras (first==last==X; Y=IV de X; X soa como
     X7; X repousa como tríade — separa de pedal de V; X no top-2 do K-S). Validado por
     simulação read-only ANTES de codar: o gatilho dispara em **1/60** e ajuda; **zero
     regressão** e **ganho líquido** (exata 74→76, relativa 81→83). Caveat: ajusta-se a n=1
     (risco de falso-positivo futuro, mitigado pelas guardas). Não toca K-S/cadência.
   - **SubV's estendidos (XXVIII c/d)** — **feito** em `extended-subv`: Chediak XXVIII c/d
     (pp.107-108). Espelho do `Dext` por 4ªJ, mas por **semitom descendente** — e com
     **detecção de cadeia**: um pré-passe (`subv_extended_indices`) acha runs maximais de
     dominantes descendo ½t, comprimento **≥3** (≥2 movimentos), e marca todos menos o
     terminal. Só a cadeia conta — o par local `F7 E7` é ambíguo com blues `IV7→III7` (foi o
     motivo do adiamento na change irmã) e **não** dispara. Membros viram `Dext` (sabor SubV),
     sem número romano, escala mixolídio; o verificador roda **antes** do gate de blues (um
     `F7` dentro da cadeia sobrepõe o `IV7 blues`); o terminal (`Db7→C`) segue `SubV` primário.
     Corrige de quebra o gap `Dext → "X"` no `FUNCTION_MACRO` do HMM (agora `"D"`,
     retroativo ao XXVIII(a)). Camada de função + roman + chord-scale + HMM; **baseline
     idêntico** (não toca `detect_key`); 349 testes (+8). Fecha a porta do semitom (XXVIII).
   - **dominantes estendidos (XXVIII(a))** — **feito** em `extended-dominants`: Chediak XXVIII
     (pp.107-108, lida do scan, offset 0). Um dominante que resolve **em OUTRO dominante** por
     4ªJ ascendente (ciclo de quintas — `A7 D7 G7 C`) pertence à **cadeia, não à tonalidade**:
     novo código `Dext`, **não leva número romano** (cifra analítica = o próprio acorde, fiel a
     "o som não está diretamente vinculado à tonalidade") e escala-acorde **mixolídio** (p.339,
     vence o default posicional lídio b7 do p.113, mas não o dominante alterado). Antes `A7→D7`
     virava `Dsec V7/II` e `Bb7→Eb7` virava `Daux`. Gate **após** o blues (I7/IV7 seguem SD/T).
     Sondagem ao vivo estreitou o escopo: o **SubV estendido** (semitom, XXVIII c/d) colide com
     o blues no par local → change própria (precisa de detecção de cadeia). Camada de função +
     roman + chord-scale; **baseline idêntico** (não toca `detect_key`); 341 testes (+7).
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

   - **(A) nomeação de modo no display** — **feito** em `modal-mode-naming`: a bifurcação
     analítica decidida em explore, parte (A). Promove o `modal_coloring.flavor` (mixolídio/
     frígio, já detectado) a um **nome de modo** fundido ao centro do `detect_key` — "D
     mixolídio" / "D frígio" — numa linha "Centro modal" ao lado da leitura tonal (markdown +
     html + explain). Pura camada de apresentação: nova função `modal_mode_name` em
     `labels.py`, render nos três alvos, **nenhuma detecção nova**. Eólio fica silencioso
     (menor natural, sem traço) e dórico fora (compartilha coleção → curadoria, não algoritmo).
     Validado ao vivo: Upa Neguinho→"D mixolídio", Canto de Ossanha→"D frígio", Wave (eólio)
     silencia, Arrastão segue "D maior"+superfície mixolídia (o dórico de Chediak é a parte
     (B)). Baseline **idêntico** por construção (86·76·83·97 · centro 100% · modulantes 100%);
     364 testes (+9).

   - **(B) anotação curada de centro modal** — **feito** em `modal-center-arbitration` via
     **Caminho 2 = anotar, não detectar** (a detecção, Caminho 1, segue bloqueada por dado —
     PROBE-FINDINGS.md). O centro modal divergente é um **fato musicológico citado**, injetado
     no display: corpus tipado `harmonic_analysis.corpus.modal_centers` com **citação
     obrigatória** (`__post_init__` + teste-invariante = gate de build), busca por identidade
     (`slug(artista)|slug(música)`), **nota do curador** no cabeçalho (MD blockquote · HTML
     `alert`+`<cite>` · JSON com citação estruturada), e um **ledger de cobertura/divergência**
     (NÃO acurácia — nada é detectado), transposição-seguro pelo intervalo curado
     `finalis_from_tonal` (não subtração absoluta). Corpus n=2: Arrastão (eixo Ré → Lá dórico,
     +7, p.125), Procissão (eixo Lá → Dó mixolídio, +3, p.126). `TIER_A_CHEDIAK` migrado p/
     ler do corpus (uma fonte). **Zero regressão tonal** provada ao vivo (86·76·83·97 · centro
     100% · modulantes 100%); 391 testes. A **bifurcação (A)+(B) está completa**.

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
| ~~3b-A~~ | ~~Nomeação de modo no display (bifurcação parte A)~~ | ~~`modal-mode-naming`~~ | ~~M~~ |
| ~~3b-B~~ | ~~Anotação curada de centro modal (bifurcação parte B, Caminho 2)~~ | ~~`modal-center-arbitration`~~ | ~~M~~ |
| ~~3c~~ | ~~Centro tonal — tier Chediak citado (Parte 4 "Tom de X"), âncora não-circular~~ | ~~`chediak-tonal-center-gold`~~ | ~~M~~ |
| ~~3d~~ | ~~"Buraco da relativa" de Coração Vagabundo — **invalidado**: o arranjo do CC repousa em Mi♭ maior (detector certo); fato mis-curado removido~~ | — | — |
| ~~4~~ | ~~Adaptador de entrada local (.txt de acordes, CC = só fonte)~~ | ~~`local-chord-input`~~ | ~~S~~ |
| ~~5~~ | ~~Reformular o baseline: CC só fonte, Chediak a base, songbook o corpus~~ | ~~`songbook-chediak-baseline`~~ | ~~M~~ |
| ~~5.5~~ | ~~Higienizar a extração (classificador de linha por densidade + whitelist por manifesto): fantasmas de letra 14%→0,5%, concordância de centro 71%→80%, invariante 62/62 mantido~~ | ~~`sanitize-chord-extraction`~~ | ~~M~~ |
| ~~6a~~ | ~~Crescer o gate funcional com o invariante VERDE de diminuto (XXI-XXII) + formalizar o de trítono~~ | ~~`grow-functional-invariants`~~ | ~~S~~ |
| 6 | **Crescer os invariantes funcionais** — restam ii-V (XIX) e cadências (XXXII). O probe (n=62) mostrou que NÃO estão verdes: viram fixes (abaixo), não gate direto | — | M |
| ~~fix-d2~~ | ~~**`fix-d2-over-attribution`**: o `D2` agora exige que o dominante RESOLVA no seu alvo (teste intervalar, pré-passe `ii_cadential_indices`). `D2` 363→199 (164 over-attributions zerados, 199 legítimos mantidos); invariantes 62/62. Pronto p/ gatear o invariante "todo `D2` resolve"~~ | ~~`fix-d2-over-attribution`~~ | ~~M~~ |
| fix-cad | **`fix-cadence-function-coherence`**: cadência×função discordam — 10 Perfeitas (9 `D→D2`, 1 `D→Dim`) onde o "I" não é codado `T`. Alinhar detector de cadência com o coder de função; só então gatear | — | S |
| 7 | **Trabalhar a worklist de corroboração** — adjudicar com Chediak, melhorar detecção sem amarrar no CC. *Parcial:* `harden-functional-center` fechou as guardas de repouso do achador funcional (dominante/inversão-como-tônica); concordância 80%→83%, worklist 12→10. Restam ~10 divergências genuínas (modo paralelo, V/relativa-como-tônica do `detect_key`) | `harden-functional-center` | M |
| 8 | Ampliar o corpus do songbook (`cifras/*.md`) — o ouro é a regra, não o gênero | — | S |
| 3b-det | Detecção de **centro** modal (Caminho 1) — **bloqueado por dado** (corpus modal melódico) | — | L |

> **Handoff (próxima sessão, pós-2026-06-30 — 4 changes fechadas):** o baseline funcional já gateia
> DOIS invariantes duros (trítono 62/62 + diminuto 62/62). Próximos passos, em ordem:
> 1. **Gatear o invariante "todo `D2` resolve no alvo"** no `songbook_baseline.py` — já VERDE
>    (0/199 violações pós-`fix-d2`), adição trivial; fecha a parte ii-V do **#6**.
> 2. **`fix-cadence-function-coherence`** — 5 incoerências `D→D2`/`D→Dim` (caiu de 10 pós-fix-d2)
>    em ah-se-eu-pudesse, ate-parece, avarandado, enquanto-a-tristeza-nao-vem, so-tinha-de-ser-com-voce;
>    o detector de cadência rotula `V→I` onde o coder chama o "I" de D2/Dim. Depois, gatear a
>    coerência de cadência fecha o **#6** inteiro.
> 3. **#7 worklist** (~10 divergências genuínas, agora erros prováveis do `detect_key`) e **#8**
>    (ampliar corpus). Ferramentas: `scripts/songbook_baseline.py` + `scripts/worklist_adjudication.py`
>    (READ-ONLY, clusteriza divergências). Medir SEMPRE ao vivo; nunca `cc_key`. **Git: tudo na
>    `main` NÃO-COMMITADO** — considerar commitar antes de seguir.

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
