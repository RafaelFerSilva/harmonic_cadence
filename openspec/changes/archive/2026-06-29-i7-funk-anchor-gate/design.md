## Context

`detect_key` roda K-S → corroboração cadencial (na `TIE_BAND`) → `_tritone_gate` →
correção de modo paralelo. O `_tritone_gate` (requirement "Functional-dominant quality gate")
corrige `Y → (Y−7)` (uma 5ª **abaixo**) quando o K-S pega o V. Aquele Abraço é o **inverso**:

```
   _tritone_gate (existente)            âncora I7-funk (esta change)
   ─────────────────────────           ─────────────────────────────
   K-S pega Y = o V                     K-S pega Y = o IV (Lá)
   tônica X = Y−7  (5ª ABAIXO)          tônica X = Y+7  (5ª ACIMA = Mi)
   Y é tensão, repousa em X             X é tônica MAS soa como dominante (I7)
   sinal: resolução funcional           sinal: ESTRUTURAL (abre+fecha em X)
   move ↓                               move ↑
```

A premissa do gate ("tônica repousa, V é tensão") é **violada** pelo I7-funk: a tônica é
tensão (I7), o IV repousa. Por isso nenhum caminho do gate dispara, e o sinal recuperador é
não-funcional. Sondagem ao vivo: K-S A=0.8943, E=0.7516 (gap 0.14 >> TIE_BAND); `B7` nunca
resolve em Mi (`B7→A`); o que codifica Mi é **first==last==E**.

**Simulação read-only (antes de codar, corpus n=60):** o gatilho base (guardas 1+2) dispara
em **1/60** (Aquele Abraço) e **ajuda** (X=E=gold); zero quebras. Guardas 3–5 satisfeitas.

## Goals / Non-Goals

**Goals:**
- Recuperar o centro Mi de Aquele Abraço (18/19 → 19/19) por um caminho estreito e principiado.
- Zero regressão das corretas (medido ao vivo).

**Non-Goals:**
- Tocar K-S, `TIE_BAND` ou corroboração cadencial.
- Generalizar para qualquer "tônica = dominante" sem o âncora first==last (risco alto).
- Detectar modo (o I7-funk é maior; reusa o modo do candidato X no K-S).

## Decisions

### D1 — Caminho separado `_i7_funk_anchor_path`, chamado no `detect_key`

Um helper novo, invocado **após** `_tritone_gate` no `detect_key`, recebendo `symbols`, o
palpite atual `(best_tonic, best_mode)` e o `ranked` do K-S (para a guarda 5). *Por quê no
`detect_key` e não dentro do `_tritone_gate`:* precisa das **alternativas** do K-S (top-2),
que o `_tritone_gate` não recebe; e é geometricamente distinto (sobe 5ª) — misturar com os
caminhos do gate (descem 5ª) confundiria a leitura. Retorna `(X_pc, mode)` ou `None`.

### D2 — As 5 guardas (conjunção estrita)

`X = first_root`; dispara só se: (1) `first_root == last_root == X`; (2) `Y == (X+5)%12`,
`X != Y`; (3) algum acorde de raiz `X` é dominante-7; (4) algum acorde de raiz `X` é tríade
maior (repouso); (5) `X` ∈ top-2 das alternativas K-S. *Por quê cada uma:* 1 = âncora
estrutural (o único sinal pró-Mi); 2 = assinatura do vamp I7-IV7 (K-S pegou o IV); 3 = a
tônica I7 funk; 4 = separa de um **pedal de V** (lá X só seria X7, nunca tríade); 5 = evita
flip selvagem. A conjunção das 5 é o que mantém o gatilho em 1/60.

### D3 — Modo do resultado = modo do candidato X no K-S

Ao corrigir para `X`, usar o modo com que `X` aparece melhor ranqueado no K-S (esperado
maior, para I7-funk). *Por quê:* manter "uma detecção de modo" (não inventar modo aqui); a
correção de modo paralelo a jusante ainda roda normalmente.

### D4 — Posição: após o tritone gate, antes da correção de modo paralelo

O âncora I7-funk e o `_tritone_gate` são mutuamente exclusivos por geometria (um sobe, o
outro desce) e por guarda (o gate exige Y só-dominante/repouso-em-X−7; o âncora exige
first==last e Y=IV). Rodar em sequência é seguro; se por acaso ambos quisessem disparar (não
ocorre no corpus), o tritone gate (mais antigo, funcional) tem precedência por vir antes.

## Risks / Trade-offs

- **[Overfit a n=1]** → o gatilho casa exatamente 1 música do corpus. Mitigação: as 5 guardas
  codificam a **teoria** do I7-funk (não a peça), e a guarda 4 (X repousa como tríade) separa
  de um pedal de V. Caveat honesto no proposal; reabrir se uma peça futura falsar.
- **[Falso-positivo futuro]** → uma peça realmente em Y que abra+feche no seu V (X), com X
  aparecendo como tríade E como X7. Improvável (terminar no V é meia-cadência, raro como fim);
  as guardas tornam isso estreito. Risco residual aceito e documentado.
- **[Baseline]** → simulação read-only já mostrou zero quebra; rodo `scripts/key_baseline.py`
  ao vivo como trava final.

## Migration Plan

1. Implementar `_i7_funk_anchor_path(symbols, ks_best, ranked)` em `key_detection.py`.
2. Chamá-lo no `detect_key` após `_tritone_gate`; aplicar `(X, mode)` se retornar.
3. Testes: Aquele Abraço (miniatura sintética: abre/fecha em E, vamp E7/A7, E tríade +
   E7, K-S pega A → corrige p/ E); guard-negativos (sem first==last; X só como X7 = pedal de
   V não dispara; Y≠IV não dispara).
4. `make test` + `make lint`; `scripts/key_baseline.py` ao vivo (centro 18/19→19/19, resto
   idêntico). Atualizar ROADMAP/AGENTS.
5. Rollback = remover o helper e a chamada.

## Open Questions

- A miniatura sintética do teste reproduz o gatilho sem rede? Sim — basta uma sequência curta
  que satisfaça as 5 guardas (ex.: `E E7(9) A7(13) E7(9) A7(13) ... E`); validar que K-S pega
  A e o âncora corrige p/ E. Se a miniatura não reproduzir o K-S=A, usar o caso real é
  inviável em teste unitário (precisa de rede) — então calibrar a miniatura na implementação.
