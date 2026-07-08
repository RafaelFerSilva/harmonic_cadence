## Context

Os ledgers de curadoria — trítono não-dominante (43) e centro `diverge` (46) — foram
100% adjudicados por humano em 2026-07-07, materializados nos corpora tipados
`corpus/tritone_adjudications.py` e `corpus/tonal_center_adjudications.py` (`Citation`
obrigatória como gate; enum fechado de veredito; `ambiguous` = resíduo honesto
declarado). A adjudicação foi **inteiramente manual** (curador + PDF do Chediak).

O projeto já provou (`ML-EVOLUTION-PLAN.md`, `PROBE-EMBEDDINGS-FINDINGS.md`) que a via
de DL não se paga: labels ínfimos (89, desbalanceados) → classificador supervisado
decora; embeddings de acorde aprendidos quebram a invariância de transposição (0.63–0.68
vs. ~1.0 do `Fingerprint` à mão) — NO-GO **arquitetural**, não de dado. A infraestrutura
de overlay existente (`overlay/similarity.py`, `overlay/clustering.py`) já faz retrieval
transposição-invariante **por construção** (reusa o `Fingerprint` de função). Esta change
aplica a mesma máquina ao problema de *acelerar a adjudicação*, não de decidi-la.

Restrições não-negociáveis (AGENTS.md, ML-EVOLUTION-PLAN §0): o símbolo/Chediak arbitra
(PRATA); fronteira de copyright (só FATOS, nunca o texto do livro); avaliação descritiva
(nunca acurácia contra o coder); isolamento de dependência (overlay-only, núcleo
stdlib-puro); mede ao vivo contra `songbook_baseline.py`.

## Goals / Non-Goals

**Goals:**
- Rascunhar (`draft`) um veredito citado para uma ocorrência suspeita, **por analogia a
  precedente já adjudicado**, com confiança visível — acelerando a próxima rodada de
  adjudicação humana a custo-zero de dado.
- Reusar a máquina de similaridade transposição-invariante existente; **zero dep nova**.
- Manter os drafts estritamente separados do corpus confirmado (só o humano promove).
- Expor um sub-uso de baixo custo: rankear candidatos à armadilha ii-V além dos 3 conhecidos.

**Non-Goals:**
- **Não** decidir nem promover vereditos automaticamente (o humano confirma).
- **Não** ingerir o PDF do Chediak (citações são herdadas do precedente confirmado).
- **Não** tocar `function_code`/`degree`/`detect_key`/os 3 gates duros/o placar de centro.
- **Não** adicionar `torch`/`gensim` nem qualquer LLM nesta fase (Fase 2 adiada).
- **Não** avaliar por acurácia contra o coder (circularidade); a métrica é confirmação humana.

## Decisions

**D1 — Case-Based Reasoning (retrieval de precedente), não classificador supervisado.**
Com 89 labels desbalanceados, um classificador decora. CBR (k-NN sobre geometria) não
treina parâmetros: usa os vereditos confirmados **diretamente** como base de casos, o que
é interpretável (o draft aponta o precedente exato + citação) e degrada com honestidade
(vizinho `ambiguous` → draft `ambiguous`). Alternativa rejeitada: regressão logística /
árvore sobre os 89 — decora, não generaliza (provado no espírito do ML-EVOLUTION-PLAN).

**D2 — Geometria de FUNÇÃO/INTERVALO como chave, não espaço de acorde absoluto.** O probe
mostrou que o espaço de acorde absoluto quebra a invariância de transposição. A chave de
retrieval é o vetor `(função, grau, qualidade, intervalo raiz→tônica, intervalo de
resolução)` — as mesmas features que já tornam o `Fingerprint` invariante. Reusa
`overlay/similarity.py` onde possível; onde a granularidade por-ocorrência não existe lá,
deriva o vetor localmente das colunas do DuckDB (grão de ocorrência já materializado).
Alternativa rejeitada: chord2vec (NO-GO, probe).

**D3 — Citação HERDADA do precedente, nunca extraída do livro.** O draft copia a
`Citation` do precedente confirmado mais próximo (um fato já curado, dentro da fronteira
de copyright). Isso respeita "só FATOS, nunca o texto" — o motor nunca lê o PDF. Um draft
sem precedente decisivo próximo (todos os `k` são `ambiguous`) sai `ambiguous`, sem
citação. Alternativa rejeitada: LLM lendo as páginas do Chediak → viola a fronteira de
copyright (adiada como Fase 2 apenas se resolvida a fronteira).

**D4 — `status="draft"` como cidadão de 2ª classe, isolado do corpus confirmado.** Os
drafts vivem só na view aditiva `v_draft_verdict` (regenerável, `DROP` = rollback). Os
corpora tipados e os `audit_*_adjudication.py` **não mudam** — continuam contando só
vereditos confirmados. Um teste-invariante garante que draft nunca vaza para a base de
casos nem para o denominador de completude. Alternativa rejeitada: um campo `draft` na
tabela de adjudicação confirmada → risco de vazamento/contaminação do gate de citação.

**D5 — Confiança = concordância dos `k` vizinhos, denominador visível.** Sem ouro para
"o draft está certo?", a única honestidade é reportar quão unânimes são os precedentes
(fração dos `k` que concordam com o mais próximo) + a distância. Não é probabilidade
calibrada — é transparência do vizinhança. Coerente com "denominador visível, nunca placar".

**D6 — Avaliação por confirmação humana (hold-out), nunca contra o coder.** A métrica de
sucesso é: dos drafts que o curador revisou, quantos confirmou. Mede-se sobre adjudicação
HUMANA nova, nunca reusando os 89 que geraram a base (evita o vazamento circular que o
ML-EVOLUTION §5 alerta). Registrado como probe, não como gate.

## Risks / Trade-offs

- **[Circularidade: drafts derivados de precedente "provando" que aprenderam o precedente]**
  → avaliação só contra adjudicação humana nova (hold-out do curador); drafts nunca entram
  na base de casos; o produto é *aceleração*, não *validação* do corpus.
- **[Base de casos pequena e desbalanceada (37 `ambiguous` no trítono; 3 `neither_ii_v`)]**
  → o CBR degrada visível: vizinho dominante `ambiguous` → draft `ambiguous` (honesto, não
  força veredito). O relatório expõe a distância — precedente distante = baixa confiança
  explícita. Não se esconde a escassez.
- **[Vazamento de draft para o corpus confirmado / auditoria]** → isolamento por view
  aditiva + teste-invariante que roda `audit_*` com e sem drafts e exige resultado idêntico.
- **[Deriva do princípio de transposição na feature de geometria]** → teste-invariante:
  ocorrência transposta produz vetor idêntico e distância 0 (o mesmo probe que matou o chord2vec).
- **[Escopo-creep para LLM-drafting]** → Fase 2 explicitamente fora desta change; nenhuma
  dep de LLM/torch/gensim entra no `pyproject`; a Fase 1 tem de provar o loop primeiro.
- **[Gate quebrar ao materializar]** → mede-se `songbook_baseline.py` ao vivo antes de
  arquivar; pausa-e-investiga se qualquer gate sair de 293/293 (esperado: inalterado, saída aditiva).

## Migration Plan

1. Implementar `overlay/precedent.py` (feature de geometria + retrieval k-NN + draft), com
   testes unitários (invariância, top-k, herança de citação, ambíguo→ambíguo).
2. Wiring aditivo: view `v_draft_verdict` em `overlay/materialize.py`; subcomando `assist`
   na CLI `corpus` + relatório em `overlay/report.py`.
3. Rodar `harmonic corpus build` (regenera derivados) e `songbook_baseline.py` — confirmar
   gates **293/293** e coder intocado.
4. Rodar `audit_tritone_adjudication.py`/`audit_center_adjudication.py` — confirmar SEM
   drift (drafts ignorados).
5. Probe de confirmação humana (amostra pequena de drafts revisada pelo curador) — registrar
   a taxa como evidência descritiva (não gate). Decidir Fase 2 (LLM) só com esse número.
- **Rollback:** `DROP VIEW v_draft_verdict` + remover `overlay/precedent.py` e o subcomando;
  nada no corpus canônico ou nos gates depende deles (saída puramente aditiva).

## Open Questions

- Distância mínima (cutoff) para emitir draft decisivo vs. cair em `ambiguous` por falta de
  precedente próximo? — calibrar no probe, começar conservador (precedente distante → ambíguo).
- Ponderar as features de geometria (função vs. grau vs. intervalo de resolução) ou usar
  cosseno uniforme como na similaridade atual? — começar uniforme (reuso), medir depois.
- A worklist pendente deve priorizar por surpresa da `v_anomaly_worklist` (Trilha B ordena o
  que a Trilha A adjudica)? — sim como ordenação default do modo varredura; barato e coerente.
