## Why

O baseline atual mede contra **um** ouro — o tom do próprio Cifra Club — o que é
honesto para a **tônica-exata absoluta** (acordes e ouro da mesma fonte ⇒ sem gap de
transposição). Mas o Cifra Club é crowdsource teórico-ingênuo: confusão relativa,
transposição por tessitura, e **miopia modal** (espreme dórico/mixolídio em maior/menor).
Para o **centro/modo**, ele não é gabarito confiável.

A falha residual do detector é justamente de **centro** entre graus diatônicos —
mediante (*Lilás* C→Em, *Açaí* G→Bm: pega o iii em vez do I) e tonal↔modal (*Arrastão*:
detecta Ré maior, Chediak diz **Lá dórico**, p.125). É um erro **estrutural, invariante a
transposição**, que a métrica de tônica-exata absoluta não isola.

Insight que torna isso barato e seguro: as duas fontes **concordam na mediante** (Cifra
Club diz *Lilás*=C = a verdade; é o detector que erra para Em) e só **divergem no modal**
(Arrastão CC=Ré maior vs Chediak=Lá dórico). Logo o Chediak-ouro **reanota** o n=60
estruturalmente — a maioria já casa com o Cifra Club — e **sobrepõe** só os poucos casos
modais, com citação de página.

Esta change é o **pré-requisito (a)** do 3b: sem o gabarito estrutural não dá para medir,
sem regressão, o gate do trítono que vem na change seguinte (`tonal-center-tritone-gate`).
Ela **não toca a detecção** — é só medição e corpus.

## What Changes

- **Segundo ouro (fatos, com proveniência):** novo fixture `(música, cc_key, offset,
  tipo, modo, provenance, justificativa)` com `provenance ∈ {chediak, verified,
  unverified}`. O `cc_key` é só **âncora de transposição**, nunca a fonte da verdade do
  centro — `offset 0` é afirmação **verificada**, não default herdado do Cifra Club. A
  métrica roda só sobre `chediak`+`verified`; `unverified` fica em quarentena (visível).
- **Métrica de acerto-de-centro (TONAL):** o harness ganha `center_accuracy` — o
  `detect_key` acertou o **centro tonal verdadeiro** (o I, não outro grau diatônico como o
  V ou o iii). É **invariante a transposição** (julga a relação de grau, não a altura
  absoluta), sobre o subconjunto **verificado por dominante funcional** (offset 0),
  reportada **ao lado** de modo/exata/relativa/coleção. O **centro modal** (offset ≠ 0) fica
  para a change de arbitragem modal: a validação mostrou que seu offset não pode vir de
  subtração absoluta (Chediak e Cifra Club podem estar em transposições diferentes).
- **Baseline:** além das 4 linhas atuais (Cifra-Club-ouro, **intactas**), imprime a linha
  de acerto-de-centro (Chediak-ouro) e um **verdict de divergência** por música quando
  Cifra Club e Chediak discordam (os casos modais), explicitando-a.
- **ROADMAP:** registrado como **3b-corpus** (pré-requisito do gate do trítono).

## Muro de copyright

O Chediak-ouro é montado **só de fatos** `(música→tom→tipo→modo)` com citação de página —
reanotação do n=60 + exemplos modais da Parte 2 (pp.121-127, já extraídos) + tons citados
**pontualmente** da Parte 4 (só o fato, com página). **NUNCA** ingere as harmonizações,
cifras ou tabelas da Parte 4 (expressão protegida). Os acordes seguem vindo do Cifra Club
(re-scrapados, não armazenados).

## Capabilities

### New Capabilities

*(nenhuma)*

### Modified Capabilities

- `key-accuracy-evaluation`: adiciona o **segundo ouro** (Chediak, centro/modo estrutural)
  e a métrica `center_accuracy` invariante a transposição, ao lado das existentes, com o
  verdict de divergência Cifra-Club↔Chediak no baseline.

## Impact

- **Novo** `scripts/chediak_structural_gold.py` — fixture de fatos (música, tônica
  estrutural, tipo, modo, página), no molde de `scripts/modal_coloring_groundtruth.py`.
- `packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py` — a
  métrica `center_accuracy` e o casamento estrutural (invariante a transposição).
- `scripts/key_baseline.py` — 5ª linha (acerto-de-centro) + verdict de divergência.
- `packages/harmonic_analysis/tests/test_key_accuracy.py` — invariância a transposição,
  concordância tonal, divergência modal registrada.
- `ROADMAP.md` — 3b-corpus. (Memória `baseline-gold-is-cifraclub` já refinada p/ 2 ouros.)
- **NÃO toca** `detect_key`/`segment_keys`/`TIE_BAND`/`cadence_corroboration` — as 4
  métricas Cifra-Club ficam **idênticas**. O gate do trítono é a change 2.
