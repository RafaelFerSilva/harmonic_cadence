## Context

A detecção de tonalidade usa Krumhansl-Schmuckler (K-S) com duas camadas de pós-processamento (Fase B): desempate cadencial (v1) e correção de modo paralelo (v2). O desempate cadencial age apenas dentro de uma "banda de empate" (`TIE_BAND`): só candidatos cujo score K-S está a menos de `TIE_BAND` do topo entram na corrida. Isso protege o K-S de ser sobreposto quando está confiante.

"Papel Marché" (João Bosco, gold=C major) falha porque:
1. A linha `"Afinação Drop D: D A D G B E"` escapa o filtro `_is_noise` e injeta 9 acordes espúrios (A, D, G, B, E), inflando o peso de Lá no perfil.
2. Mesmo sem esse ruído, o gap K-S entre A minor (0.87) e C major (0.78) é ~0.08, acima de `TIE_BAND=0.06`.
3. A corroboração cadencial já produz o sinal certo (C major=7.00 vs A minor=0.00) mas C major nunca entra na banda.

## Goals / Non-Goals

**Goals:**
- Filtrar linhas de afinação/instrumento no `clean_cifra_lines` de `cifra_core`.
- Recalibrar `TIE_BAND` para 0.10, cobrindo o gap de Papel Marché com ou sem ruído de afinação.
- Confirmar via baseline (n=60, rede) que a mudança corrige Papel Marché sem regressões.
- Adicionar teste unitário para a nova regra de filtro de afinação.

**Non-Goals:**
- Alterar a lógica de `cadence_corroboration` ou `_correct_parallel_mode`.
- Modificar os pesos `ROOT_WEIGHT`, `CADENCE_WEIGHT` ou os parâmetros de corroboração.
- Cobrir outros tipos de ruído de cifra além de linhas de afinação.
- Resolver os casos residuais Djavan (Incremento 3 do roadmap).

## Decisions

### D1 — Onde filtrar a linha de afinação: `lines.py` (cifra_core), não `analysis_service`

O filtro canônico de linhas vive em `cifra_core/lines.py` (`clean_cifra_lines`) e é a única fonte de verdade para o que é ruído estrutural. Adicionar a regra lá garante que o filtro seja idempotente e aplicado uma única vez, independente do adaptador (in-process ou HTTP). Alternativa descartada: filtrar no `_extract_chords` do `analysis_service` — duplicaria a responsabilidade e quebraria o contrato D3 (filtragem canônica no `cifra_core`).

**Implementação:** adicionar em `_is_noise`:
```python
_AFIN_RE = re.compile(r"(afinac|drop\s+[a-g]|capotraste)", re.IGNORECASE)
```
O padrão `drop\s+[a-g]` evita falsos positivos em linhas de letra que contenham "drop" (ex.: "a raindrop"); exige que "drop" seja seguido de uma nota de instrumento (A–G). "Capotraste" é inequívoco. "Afinac" (base de "afinação") também.

### D2 — Valor de TIE_BAND: 0.10

Gap medido com chords limpos: ~0.083. Gap com ruído de afinação: ~0.099. `TIE_BAND=0.10` cobre ambos com margem mínima. Valores considerados:

| Valor | Cobre gap limpo? | Cobre gap com ruído? | Risco de sobrepor K-S confiante |
|-------|:---:|:---:|:---|
| 0.07  | não | não | baixo |
| 0.09  | sim | não | baixo |
| **0.10** | **sim** | **sim** | **baixo-moderado** |
| 0.12  | sim | sim | moderado |

`TIE_BAND=0.10` escolhido: defensivo contra ruído residual sem alargar demais a banda. A proteção contra sobrepor K-S confiante é estrutural — quando K-S está correto, a corroboração concorda ou empata em zero, e o segundo critério do `max()` (score K-S) preserva a resposta.

### D3 — Não alterar o gate de âncora-baixo nem os pesos de corroboração

A Fase B v2 usa um gate explícito (o último baixo ou uma cadência V/SubV→tônica) antes de inverter o modo. Esse gate não é afetado por `TIE_BAND` — ele age *após* a escolha do candidato vencedor. Ampliar a banda muda apenas *quem concorre*, não a lógica de desempate.

## Risks / Trade-offs

- **Risco: regressão em música com gap K-S entre 0.06–0.10 onde K-S é correto e corroboração aponta errado.** Mitigação: a corroboração só pontua quando há sinais funcionais reais (1º acorde, acorde final, cadência autêntica). Uma música onde K-S está correto tem esses sinais apontando para a tonalidade correta também. O tie-break secundário é o score K-S, que preserva a resposta certa no empate de corroboração. Validação empírica obrigatória: baseline n=60.

- **Risco: `_AFIN_RE` com falso positivo em linha de letra.** Mitigação: padrão conservador — `"afinac"` e `"capotraste"` são específicos de contexto musical/instrumento; `"drop\s+[a-g]"` exige a letra de nota logo após.

- **Trade-off: TIE_BAND é um hiper-parâmetro exposto como constante.** O valor 0.10 foi escolhido contra o corpus n=60, mas o corpus crescerá. Documentar que esse valor é recalibrável e deve ser revisitado ao dobrar o corpus.

## Open Questions

- Após o baseline confirmar sem regressões, vale atualizar o comentário em `key_detection.py` que referencia o corpus de calibração (hoje diz "test_key_corpus", que é sintético)?
- Existem outras cifras no corpus n=60 com linhas de afinação que também poluem o perfil? (Só saberemos rodando o baseline antes/depois e comparando perfis individuais.)
