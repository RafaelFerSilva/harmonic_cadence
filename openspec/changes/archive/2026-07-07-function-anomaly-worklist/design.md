## Context

O corpus está materializado em `corpus.duckdb` (11 tabelas, grão = ocorrência de acorde;
`chord_occurrence` traz `song_id`, `position`, `symbol`, `degree`, `function_code`, `strength`,
`roman_numeral`). O vocabulário funcional tem **12 símbolos** e o corpus tem **~48k ocorrências /
293 músicas / 702 trigramas distintos**, com cauda clara de trigramas de contagem 1 — sinal de
surpresa já observável. A view `v_function_trigram (fn1,fn2,fn3,n)` já existe. Restam duas
worklists de curadoria (`v_ledger_tritone_nondominant` = 43; `v_center_ledger` diverge = 46) que
hoje são adjudicadas contra o Chediak sem priorização.

Restrição de método (inviolável): o Cifra Club é só fonte; o Chediak é a base; o motor simbólico é
o ouro. Toda mudança mede contra `songbook_baseline.py` ao vivo; gate quebrado = pausa-e-investiga.
O banco é view materializada, nunca ouro.

## Goals / Non-Goals

**Goals:**
- Um overlay estatístico **interpretável** que ranqueia ocorrências por surpresa funcional e
  **prioriza** as worklists de trítono/centro para a adjudicação Chediak.
- Estritamente subordinado ao símbolo (PRATA): rankeia, não arbitra; discordância é sinal.
- Derivado/regenerável, materializado como view; relatório PT-BR com denominador visível.
- Mede-se contra o baseline ao vivo; zero regressão nos 3 gates duros e no `detect_key`.

**Non-Goals:**
- NÃO prever/reescrever `function_code` como verdade (isso seria circular e violaria a lei de ferro).
- NÃO deep learning / embeddings nesta change (fica para a change seguinte de similaridade).
- NÃO tocar detecção de centro, cadência, gates, nem o pipeline do motor.
- NÃO avaliar o modelo por "acurácia contra o coder" (o coder É o ground truth — não há placar).

## Decisions

**D1 — n-grama suavizado, não rede neural.** Vocabulário de 12 tokens + 48k amostras: um LM de
trigrama com backoff (Witten-Bell, robusto para vocab pequeno e sem tuning) é suficiente, 100%
interpretável e citável (cada surpresa se explica por contagens observáveis). *Alternativas:* rede
neural / HMM treinado — rejeitados: pouco dado, caixa-preta, e o motor já tem um HMM funcional
simbólico (não competir). Manter stdlib (`math`) + agregação em DuckDB; sem dependência ML pesada.

**D2 — surpresa = −log P(fn | contexto), não anomalia por clustering.** A surpresa condicional é
diretamente interpretável ("esta função é rara aqui") e alinha com a pergunta da adjudicação. O
contexto default é o par anterior (trigrama fn₋₂,fn₋₁→fn) com backoff para bigrama/unigrama.
*Alternativa:* isolation forest / autoencoder sobre features — rejeitado: menos interpretável, mais
dependência, e a worklist precisa de *explicação*, não só de flag.

**D3 — worklist é view SQL derivada, materializada pelo mesmo padrão da persistência.** O overlay
computa o modelo em Python, grava uma tabela de escores por ocorrência (ou `CREATE OR REPLACE VIEW`
a partir de uma tabela de escores) e expõe `v_anomaly_worklist` cruzando com os ledgers. Segue o
contrato existente (regenerável por run; nunca ouro). *Alternativa:* tudo em SQL puro — tentador
(o trigrama já existe como view), mas o backoff suavizado é mais limpo/testável em Python; a
materialização final é SQL.

**D4 — subpacote novo `harmonic_analysis/overlay/`.** Isola o overlay do `domain/` (símbolo) e do
`persistence/` (materialização base). Módulos: `model.py` (contagem+backoff+surpresa),
`materialize.py` (escreve escores + view), `report.py` (Markdown PT-BR). CLI: `harmonic corpus
anomalies` em `cli/main.py`, ao lado de `corpus build|gates|report`.

**D5 — guarda-corpo anti-placar reaproveitado.** O `corpus report` já tem teste que barra
vocabulário de placar; o relatório de anomalias herda o mesmo teste (lista com denominador; frase
fixa "o ML rankeia, o Chediak adjudica").

## Risks / Trade-offs

- **[Circularidade — treinar e medir no mesmo coder]** → Mitigação: o overlay NUNCA é avaliado por
  acurácia contra o coder; seu produto é uma *worklist de discordância*, e discordância é o sinal
  desejado (não erro). Nenhum rótulo é alterado. É isto que torna o uso legítimo.
- **[Surpresa ≠ erro — muita anomalia é MPB legítima e rica]** → Mitigação: o relatório declara que
  a worklist é *candidata a olhar*, o Chediak decide; cruzamento com os ledgers foca no que já é
  suspeito por teoria, reduzindo falso-positivo de curadoria.
- **[Esparsidade em 293 músicas infla surpresa de trigramas raros porém válidos]** → Mitigação:
  backoff/suavização; reportar a contagem observada ao lado da surpresa (denominador visível) para
  a curadoria calibrar; considerar cutoff mínimo de contexto.
- **[Drift do overlay vs. run do banco]** → Mitigação: o overlay carimba `run_id`/`engine_version`;
  regenerável; falha-rápido se rodar contra run inexistente.
- **[Regressão silenciosa nos gates]** → Mitigação: a change roda `songbook_baseline.py` ao vivo
  antes/depois; a spec exige 293/293 mantido e nenhum `function_code` alterado.

## Migration Plan

1. Materialização é aditiva: `CREATE OR REPLACE VIEW v_anomaly_worklist` + tabela de escores nova.
   Rollback = `DROP` da view/tabela; o resto do banco é intocado.
2. Sem migração de schema das 11 tabelas-base. Sem mudança de dependências de runtime obrigatórias.
3. Regeneração via `harmonic corpus anomalies --rebuild` (ou implícito no primeiro run sobre o run
   corrente do banco).

## Open Questions

- **Ordem do n-grama:** trigrama com backoff é o default; validar contra bigrama no probe (o vocab
  de 12 pode preferir bigrama para densidade). Decidir na implementação medindo cobertura de
  contexto, não acurácia.
- **Contexto simétrico vs. causal:** usar só passado (fn₋₂,fn₋₁) é mais simples e suficiente para a
  worklist; um contexto bilateral (também fn₊₁) pode afinar a surpresa. Começar causal; deixar
  bilateral como follow-up se a curadoria pedir.
- **Feature adicional `degree`/`strength`:** v1 usa só `function_code`; enriquecer com grau é um
  follow-up (mais poder, menos interpretável) — fora do escopo desta change.
