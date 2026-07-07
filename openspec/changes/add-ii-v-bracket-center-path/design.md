## Context

O gate de qualidade do `detect_key` (`_tritone_gate`) já corrige o V-como-tônica por 3 paths
puramente estruturais (A exclusivo-dominante, B ancorado, C cadencial-na-abertura). A adjudicação
de centro isolou uma 4ª falha — a **armadilha do ii-V** (3 músicas): vamp `ii-V` onde o K-S pega o
**V** e o achador funcional pega o **ii**, nenhum pega o **I**.

Investigação empírica (simulação `detect_key` sobre as 293 no scratchpad):
- Path A falha: o V (Y) repousa 1× como acorde menor (Gm/Cm) → não é "exclusivamente dominante".
- Paths B/C falham: o I (X) **não é o 1º acorde** — a peça abre no **ii** (Dm/Dm/Gm).
- Gate estrutural ingênuo ("abre em ii-V", ou "abre em ii-V + repouso(X)>repouso(Y)") **REGRIDE**:
  quebra `ceu-e-mar`/`pouca-duracao` (agree) e `feitinha-pro-poeta` (detect-certo) — todos "abrem
  em ii-V-do-IV" legítimo.
- Gate "detect = V do funcional" **REGRIDE** `chora-tua-tristeza` (detect=Ré é certo; Ré é V de Sol).
- **Bracket** ("detect=V de X E funcional=ii de X"): dispara em **exatamente** `bolinha`/`menina`/
  `rio` → Dó/Dó/Fá, **zero falso-positivo em 293**.

## Goals / Non-Goals

**Goals:**
- Corrigir o `detect_key` na armadilha ii-V com **zero regressão** (provado por simulação).
- Discriminador citável (Chediak pp.84-85) e específico (usa os dois métodos).

**Non-Goals:**
- **NÃO** corrigir o achador funcional (mover o placar 216/262) — 2º subsistema do OURO, fora de
  escopo (decisão do usuário registrada).
- **NÃO** tratar os `V↔I` onde o funcional já acerta (`me-perdoe-maria`: detect=V, funcional=I) —
  geometria diferente (não é bracket; e "detect=V do funcional" regride `chora-tua-tristeza`).
- **NÃO** tocar Paths A/B/C nem o i7-funk.

## Decisions

**1. Novo path que consulta o achador funcional — a exceção citada à regra "estrutural".**
Os A/B/C são estruturais por design (desacoplados). O #7 provou que nenhum gate estrutural separa a
armadilha de um ii-V-do-IV. O bracket precisa saber que o funcional pegou o **ii** — logo consulta
`chediak_functional_center`. *Alternativa descartada:* reimplementar a lógica do ii no domínio —
duplicaria o achador e divergiria dele; consultar a fonte única é mais honesto.

**2. Import tardio + pré-condições baratas primeiro.**
`chediak_functional_center` é importado dentro da função (não no topo do módulo) e chamado só depois
de as pré-condições baratas valerem (Y candidato a V, ≥2 V7→X, X presente). Sem ciclo de import
(`functional_center` → só `cifra_core`) e sem recursão (`functional_center` não chama `detect_key`).
Custo no caminho comum ≈ zero.

**3. Guard de repouso relaxado (≥1), compensado pela especificidade do bracket.**
Nos vamps a tônica aparece tanto dominante-colorida (`I7`/`C9`) quanto como `C7M`, então o
`repouso>dominante` dos B/C mata bolinha/menina (medido). Como o bracket (dois métodos concordando
no pré-tônica de X) já é altíssima-especificidade, basta `X` repousar ≥1×. Simulação confirma:
mesmo relaxado, só os 3 disparam.

**4. Corrige o detector, não o placar — documentado.**
Pós-fix: detect=I, funcional=ii → ainda divergem no ledger. O gate melhora a CORREÇÃO do detector
(alinha à teoria/adjudicação), não a concordância. Registrado na spec (cenário dedicado) para não
induzir a leitura de "subiu o placar".

## Risks / Trade-offs

- **[Falso-positivo futuro ao crescer o corpus]** → o corpus está congelado em n=293 e a simulação
  cobre-o inteiro (só 3 disparam). Se um dia crescer, a assinatura bracket é intrinsecamente
  específica (exige os dois métodos cercando o mesmo X + ≥2 resoluções). Mitigação: um teste que
  re-simula e falha se o conjunto de disparos ≠ {bolinha, menina, rio}.
- **[Acoplamento domain→validation]** → real, mas unidirecional e sem ciclo (verificado); import
  tardio isola. É a exceção citada, contida a um path.
- **[Custo de chamar o funcional]** → guardado por pré-condições baratas; n=293 trivial.

## Migration Plan

1. Implementar `_ii_v_bracket_path` + wiring no `detect_key` (após `_tritone_gate`).
2. Teste unitário (bolinha/menina/rio corrigidos; ceu-e-mar/feitinha/chora NÃO tocados) + teste de
   "conjunto de disparos == os 3" (anti-regressão sobre o corpus).
3. `songbook_baseline.py` ao vivo: 3 gates 293/293, corroboração 216/262 inalterada, 8 detect-certos
   intactos. Rebuild do DuckDB + gates.
Rollback: remover o path (os A/B/C e todo o resto ficam idênticos).

## Open Questions

- Nenhuma bloqueante. O follow-up natural (fora de escopo) é o achador funcional preferir o alvo do
  ii-V ao ii — aí os 3 virariam agree (placar 216→219); decisão do usuário para outra change.
