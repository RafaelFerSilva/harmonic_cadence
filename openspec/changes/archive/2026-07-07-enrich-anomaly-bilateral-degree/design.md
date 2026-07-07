## Context

O overlay v1 pontua surpresa causal (fn₋₂,fn₋₁→fn) sobre um único canal (`function_code`),
materializado em `anomaly_score` + `v_anomaly_worklist`. O probe (run 5, n=15343) confirmou:
`degree` está 85% populado, 18 valores distintos (+ `∅` para os 15% nulos) — escala comparável às
12 funções, esparsidade gerenciável. O `FunctionalSequenceModel` já é um n-grama Witten-Bell
genérico sobre tokens de string — nada nele é específico de "função", então serve para grau e para
a direção reversa sem reescrita do núcleo.

## Goals / Non-Goals

**Goals:**
- Surpresa **bilateral** (média causal+reversa) e **bi-canal** (função + grau), com componentes
  visíveis — afia a worklist que alimenta a adjudicação Chediak.
- Zero regressão: 3 gates duros 293/293, `function_code`/`degree` do coder intocados (PRATA).
- Determinístico, derivado, regenerável; sem dependência nova.

**Non-Goals:**
- NÃO token conjunto (função×grau) — explodiria o vocabulário (12×19) e esparsificaria demais no
  corpus de 293 músicas. Dois canais independentes combinados é a escolha.
- NÃO pesos aprendidos entre canais/direções nesta change (média simples; re-ranque manual fica
  possível pelos componentes expostos).
- NÃO tocar detecção, gates, ou o pipeline do motor.

## Decisions

**D1 — modelo backward = mesmo modelo sobre sequências revertidas.** `FunctionalSequenceModel` já
é agnóstico ao token; treinar uma segunda instância sobre `reversed(seq)` dá o modelo reverso sem
código novo de contagem. A surpresa reversa da posição `i` é a surpresa da posição espelhada
`L−1−i` na sequência revertida. *Alternativa:* um modelo bidirecional "de verdade" (cloze/MLM) —
rejeitado: caixa-preta, dependência, e o corpus é pequeno; duas cadeias interpretáveis bastam.

**D2 — combinação por MÉDIA em bits, componentes expostos.** Surpresa de canal =
mean(causal, reversa); `surprise_bits` = mean(função, grau). Bits são a unidade natural de surpresa,
então a média é dimensionalmente limpa e simétrica; um acorde anômalo dos dois lados / nos dois
canais sobe suavemente. Expor `surprise_function`/`surprise_degree` mantém o "denominador visível"
e permite re-ranque manual. *Alternativa:* max (só o pior canal) ou soma — média é mais estável e
interpretável; soma dobraria a escala sem ganho.

**D3 — grau: token cru + sentinela `∅` para NULL.** Os 18 graus crus (com `°`, acidentes `bVII`,
`#IV`) já carregam o sinal útil; `∅` para "sem grau diatônico" é ele mesmo informativo (acorde
fora de escala). Não depender de `degree_base` (normalização é preocupação de outra view).
*Alternativa:* `degree_base` (strip de qualidade) — descartado: perde `°`/acidente, que é justo o
que interessa para anomalia.

**D4 — `surprise_bits` muda de semântica (BREAKING interno, aceitável).** v1 = causal-função; v2 =
média bilateral função+grau. É derivado/regenerável; a mudança é rematerializar. Os testes que
fixavam a semântica causal são atualizados (não removidos) para a bilateral.

## Risks / Trade-offs

- **[Grau nulo (15%) polui o canal]** → Mitigação: `∅` é token de 1ª classe (informativo, não
  ruído); a suavização Witten-Bell trata `∅` como qualquer token; o componente de grau fica
  exposto para a curadoria discontá-lo se quiser.
- **[Média mascara um canal muito anômalo]** → Mitigação: os componentes ficam visíveis e a view
  os expõe; um follow-up pode oferecer ordenação por max/componente sem mudar o schema.
- **[Backward duplica custo de treino]** → Mitigação: n-grama sobre 15k ocorrências e vocab ≤19 é
  trivial (ms); custo desprezível.
- **[Regressão silenciosa nos gates]** → Mitigação: baseline ao vivo antes/depois; a spec exige
  293/293 e nenhum `function_code`/`degree` alterado (o overlay só LÊ).

## Migration Plan

1. `anomaly_score` ganha colunas (`surprise_function`, `surprise_degree`); `CREATE TABLE IF NOT
   EXISTS` + rematerialização recria o schema no rebuild. Se a tabela antiga existir sem as colunas,
   `DROP TABLE anomaly_score` antes do rebuild (documentado no handler) — é derivado, sem perda.
2. `v_anomaly_worklist` é `CREATE OR REPLACE` (aditivo). Rollback = rematerializar a v1.
3. Sem migração de dado externo; sem mudança nas 11 tabelas-base.

## Open Questions

- **Peso função×grau:** média 50/50 é o default honesto. Se a curadoria achar o grau ruidoso,
  um `--weight` ou ordenação por componente é follow-up (schema já expõe os componentes).
- **Contexto de grau bilateral vs. causal:** por simetria, o grau também é bilateral. Se provar
  redundante, colapsar para causal é trivial (menos um modelo).
