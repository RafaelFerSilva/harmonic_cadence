## Context

`cluster_traits` hoje soma a distribuição de função e as cadências dos membros e mostra as top —
absolutas. Como T/SD/D dominam o corpus, toda família grande exibe as mesmas, e o traço não
distingue nada. O `fingerprint_from_db` já dá a distribuição de função por música; o baseline do
corpus é a média dessas distribuições.

## Goals / Non-Goals

**Goals:**
- Traço de família = o que ela tem A MAIS que o corpus (lift), com o valor visível.
- Sinalizar a família-baseline (sem traço distintivo) em vez de inventar um.
- Zero dependência nova; descritivo; zero regressão.

**Non-Goals:**
- NÃO materializar traços (é barato computar na consulta).
- NÃO TF-IDF sofisticado nesta change — lift simples (diferença de médias) é interpretável e basta.
- NÃO mudar o algoritmo de clustering nem o schema.

## Decisions

**D1 — lift = média_família(f) − média_corpus(f), por função e por cadência.** Diferença de
participações médias: positivo = sobre-representado. Interpretável, com denominador (mostro o lift).
*Alternativa:* razão (família/corpus) — infla funções raras (divisão por ~0) e é menos legível;
diferença é mais estável. TF-IDF é overkill p/ 12 funções.

**D2 — baseline do corpus computado UMA vez por chamada.** Média das distribuições de função das M
músicas (e taxa de cadências), reusada para todas as famílias. O(M) fingerprints, já baratos.

**D3 — família-baseline sinalizada.** Se nenhum lift > 0 (a família É a média), a saída diz isso
explicitamente. Evita o engano de listar "T, SD, D" como se fosse característico.

**D4 — cadências por taxa comparável.** Para cadência uso a taxa por música (nº de cadências da
família / músicas da família) vs. a mesma taxa no corpus, para o lift ser comparável entre famílias
de tamanhos diferentes.

## Risks / Trade-offs

- **[Lift de família pequena é ruidoso]** → Mitigação: mostro o tamanho da família ao lado (o
  usuário calibra); um mínimo de suporte é follow-up.
- **[Diferença de médias favorece funções de participação alta]** → Mitigação: aceitável p/ v1
  (queremos o que domina A MAIS); normalizar por desvio é follow-up sem mudar a interface.

## Migration Plan

1. Só código (consulta/CLI); sem schema, sem dependência. Rollback = reverter a função.

## Open Questions

- **Quantos traços mostrar / cutoff de lift:** top-3 com lift > 0; um cutoff mínimo de lift é
  follow-up se a saída ficar ruidosa.
