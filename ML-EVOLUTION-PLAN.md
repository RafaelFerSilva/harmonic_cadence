# Plano de evolução ML/DL — do platô simbólico às representações aprendidas

> **Status:** plano técnico para decisão (2026-07-07). NÃO é uma change aprovada.
> Escrito a pedido: detalhar as 3 frentes de DL (arquitetura, dados, riscos,
> dependências) para o usuário decidir depois. A decisão de stack ficou comigo,
> justificada aqui.
>
> **⚠ ATUALIZAÇÃO (probe Fase 0 rodado — ver `PROBE-EMBEDDINGS-FINDINGS.md`):**
> **Frente A (embeddings de acorde aprendidos) = NO-GO.** Medido ao vivo: chord2vec
> quebra a invariância de transposição (0.63–0.68 vs. 1.0 do Fingerprint à mão) e não
> supera o baseline. O gargalo é **arquitetural**, não de dado — transferência externa
> (Frente B) não resolveria. DL não se paga por esta via. Maior retorno segue sendo a
> adjudicação humana (mais labels), não DL nem dado novo.

## 0. As leis que restringem TODA frente de ML aqui (não-negociáveis)

Qualquer coisa aprendida entra como **PRATA**, subordinada ao símbolo:

1. **O símbolo/Chediak adjudica.** O ML **rankeia/descreve/prioriza**; NUNCA reescreve
   `function_code`/`degree`, NUNCA arbitra centro, NUNCA toca os 3 gates duros nem o
   `detect_key`. Discordância é sinal, não erro.
2. **Mede-se ao vivo** contra `songbook_baseline.py`; pausa-e-investiga se um gate quebra.
3. **Nada de placar inflado.** Denominador visível; descritivo, não acurácia contra o coder.
4. **Isolamento de dependência.** Peso de DL vive só em `overlay/` (ML), nunca no núcleo
   simbólico (`cifra_core`, `domain/`, `validation/`), que segue stdlib-puro.

## 1. A realidade do dado (o fato que define tudo)

Medido no `corpus.duckdb` (n=293):

| Métrica | Valor | Implicação para DL |
|---|---|---|
| Músicas | **293** | Amostras de nível-música minúsculas (embeddings de música ⇒ derivar, não aprender direto) |
| Ocorrências de acorde | **15.343** | ~15k tokens — **ínfimo** para LM neural (LMs treinam em bilhões) |
| Transições | **~15.050** | idem |
| Vocabulário de acorde distinto | **740** | 15k tokens / 740 tipos = **muito esparso**: chord2vec do-zero não aprende bem |
| Vocabulário de FUNÇÃO | **~14** | Denso o bastante; o n-grama Witten-Bell já é quase-ótimo aqui |

**Conclusão honesta (o eixo do plano):** neste tamanho, **DL do-zero tende a empatar ou
perder** para o que já temos (n-grama Witten-Bell sobre função; `Fingerprint` à mão com
priors fortes). O valor real do DL está **condicionado a TRANSFERÊNCIA** (importar
conhecimento de corpus externo grande). Sem isso, é peso sem ganho. Por isso a Frente B
(pré-treino/transferência) não é "mais uma frente" — é a **condição de viabilidade** das
outras duas.

Corolário de método (o mesmo que nos salvou 2× nesta sessão — matou o Path D ingênuo e o
fix do achador funcional): **PROBAR o ganho antes de comprometer stack.** Não adicionar
PyTorch na fé; medir o lift primeiro.

## 2. Decisão de stack (minha, justificada)

**Recomendação: entrada em duas fases, peso proporcional à prova de ganho.**

- **Fase 0 — probe leve (sem PyTorch):** `chord2vec` estilo skip-gram via **`gensim`**
  (ou numpy puro), pré-treinado em corpus externo de cifras, testado como substituto do
  `Fingerprint` na similaridade/clustering. Objetivo único: **medir o lift** dos embeddings
  aprendidos vs. o à mão, com uma métrica descritiva honesta (ex.: coerência dos vizinhos
  contra os traços de família já validados). Dependência: `gensim`+`numpy` (moderada, isolada
  em `overlay/`).
- **Fase 1 — PyTorch, SÓ se a Fase 0 provar ganho:** modelo de sequência neural
  (LSTM/Transformer pequeno) para surpresa + embeddings contextuais. `torch` é a dep pesada;
  entra **apenas** com evidência de que supera o n-grama, e **só** em `overlay/` (import
  tardio; o núcleo nunca importa torch).

Justificativa: respeita a lei #4 (isolamento) e o ethos stdlib do projeto (adiciona peso só
quando provado), e é coerente com a disciplina "medir antes de construir". Uma métrica de
avaliação **descritiva** (não acurácia contra o coder) tem de ser desenhada junto — ver riscos.

## 3. Frente A — Overlay neural + embeddings aprendidos

**O que evolui:** `overlay/model.py` (LM n-grama Witten-Bell, `FunctionalSequenceModel`/
`BidirectionalModel`) e o `Fingerprint` à mão de `domain/style_fingerprint` (vetor concatenado:
distribuição de função + matriz de transição + cadências + modal + tensão).

**Arquitetura proposta:**
- **Nível função (14 símbolos):** modelo de sequência pequeno (LSTM 1 camada / mini-Transformer)
  → surpresa −log P(fn|contexto) por ocorrência, alimentando a `v_anomaly_worklist`.
  *Expectativa honesta:* ganho **marginal** sobre o Witten-Bell (vocab denso, o n-grama já é bom).
- **Nível acorde (740 símbolos):** embeddings de acorde aprendidos (skip-gram/contextual),
  **pré-treinados externamente** (Frente B) e fine-tunados nas 293. É **aqui** que o DL pode
  ganhar de verdade — o espaço de 740 acordes é onde o método à mão é mais fraco.
- **Nível música:** embedding por música = **pooling** dos embeddings de acorde/função
  (média/atenção), NÃO aprendido direto (293 amostras). Substitui/aumenta o `Fingerprint` na
  `overlay/similarity.py` e `overlay/clustering.py`.

**Entregável PRATA:** mesma superfície de hoje (`corpus anomalies`/`similar`/`clusters`), com
o motor de representação trocado; comparação lado-a-lado com o baseline à mão (mantém ambos até
o aprendido provar ganho). Transposição-invariância: preservar via features de função OU
treinar com augmentation por transposição (12 tons) — decisão de design.

**Riscos:** (a) overfit (15k tokens) → regularização forte, transfer obrigatório, early-stop
por validação; (b) perda de interpretabilidade → manter o `Fingerprint` à mão como baseline
sempre visível; (c) transposição → augmentation ou features de função.

## 4. Frente B — Transferência / pré-treino em corpus externo (o linchpin)

**Por que existe:** a Seção 1 mostra que sem conhecimento externo, o Dl não se justifica.

**Fontes candidatas (cifras/acordes, licença a verificar caso a caso):**
- **Chordonomicon** (2024, ~680k músicas com sequências de acordes) — a maior; ideal p/ pré-treino.
- **iReal Pro / jazz standards** (~1.3k) — vocabulário harmônico rico (ii-V-I, secundários,
  SubV) — **alto overlap com a MPB**.
- **McGill Billboard / SALAMI** (~1k, anotação de acordes revisada).
- **Hooktheory/Theorytab** (grande, acorde+melodia; foco pop).

**Pipeline:** normalizar o vocabulário de acorde externo → o MESMO parser (`cifra_core.theory`)
→ pré-treinar os embeddings/o modelo de sequência → **fine-tune** nas 293 (MPB). Importa-se
**representação, não rótulo** — o Chediak segue árbitro; o corpus externo NUNCA vira ouro.

**Caveat honesto — domain shift:** jazz/pop ≠ bossa. A estatística de transição (ii-V-I,
dominantes secundários) transfere razoavelmente (vocabulário compartilhado), mas o "sotaque"
da bossa (empréstimo modal, SubV, tônica I7) é próprio. O fine-tune nas 293 é o que ancora no
dialeto; medir se a transferência ajuda ou atrapalha é parte do probe (Fase 0).

**Fronteira de dado/licença:** verificar licença de cada corpus externo antes de ingerir;
registrar proveniência; o corpus externo é **insumo de representação**, gitignored como os
songbooks, nunca entra no baseline funcional (que é só MPB+Chediak).

## 5. Frente C — Cabeça supervisionada nos rótulos adjudicados

**O que usa:** os corpora de adjudicação desta sessão como **labels reais**:
`tritone_adjudications` (43: 6 chromatic + 37 ambiguous) e `tonal_center_adjudications`
(46: 28 functional / 8 detect / 3 neither_ii_v / 4 modulating / 3 ambiguous).

**Ideia:** um classificador pequeno (features harmônicas → veredito) que **generaliza** as
regras que hoje escrevemos à mão — ex.: aprender sozinho o padrão "armadilha ii-V" (que o Path D
codificou à mão via bracket) e propor candidatos ALÉM dos 3 conhecidos, como **ranking PRATA**
para a próxima rodada de adjudicação humana.

**O problema honesto — labels ínfimos:** 43 + 46 = 89 exemplos, com classes desbalanceadas
(37 ambiguous; 3 neither_ii_v). Isso é **pequeno demais** para treino supervisado sério; um
classificador aqui **decora**, não generaliza. Portanto:
- **Não é a 1ª frente.** Vira útil só quando os labels crescerem — o que depende da **adjudicação
  humana** (você, com o PDF) promover os `ambiguous` a decisivos, expandindo o conjunto rotulado.
- Enquanto isso, a versão viável é **few-shot / regras-fracas**: usar os 89 como *seeds* para
  um esquema de weak-supervision (Snorkel-like) ou para *prompting* de um LLM que rascunha
  vereditos citados em escala — um "neuro-assist" à adjudicação simbólica (foi, na prática, o
  que fiz à mão nesta sessão).

**Risco central:** circularidade e vazamento — treinar em labels que saíram de regras e "provar"
que aprendeu as regras. Mitigação: avaliar só contra adjudicação HUMANA nova (hold-out do curador),
nunca contra o coder.

## 6. Sequência sugerida (dependências entre frentes)

```
Fase 0  Probe (gensim/numpy): chord2vec pré-treinado externo  ──┐
        vs. Fingerprint à mão, métrica descritiva de vizinhos   │  (decide se DL se paga)
                                                                 ▼
Fase 1  SE ganho provado → Frente B (pré-treino sério) + Frente A (overlay neural + embeddings)
                                                                 │
Fase 2  Frente C (classificador) — só quando os labels adjudicados crescerem (adjudicação humana)
```

- **Frente B é pré-requisito de A** (sem transfer, A não se paga — Seção 1).
- **Frente C depende de mais labels** (adjudicação humana), não de mecanismo — data-gated, como
  o modal-center já foi.
- Cada fase mede ao vivo (gates 293/293) e mantém o método à mão como baseline visível.

## 7. Riscos transversais e o que NÃO fazer

- **Não** trocar o símbolo por embedding em lugar nenhum do caminho de decisão (viola a lei #1).
- **Não** adicionar `torch` antes da Fase 0 provar ganho (viola "medir antes de construir").
- **Não** deixar o corpus externo contaminar o baseline funcional (só MPB+Chediak).
- **Não** avaliar por acurácia contra o coder (circularidade); a métrica é descritiva/hold-out humano.
- **Métrica de avaliação é o subproblema mais difícil:** "o embedding aprendido é melhor?" não tem
  ouro óbvio (similaridade ≠ qualidade). Desenhar a métrica descritiva honesta é parte da Fase 0,
  não um detalhe.

## 8. Nota sobre o Vol. II (contexto desta decisão)

O Vol. II (`base_estudo/`) é **companion aplicado** (dicionário de acordes/escalas + dedilhado +
70 músicas), não novo tratado teórico. **Não** reabre o modal-center (segue bloqueado por dado).
Uso legítimo: validar/completar `chord_scale` e os clichês harmônicos; +70 músicas como ouro de
validação (copyright — referência, não ingestão). Ortogonal a este plano de DL.
