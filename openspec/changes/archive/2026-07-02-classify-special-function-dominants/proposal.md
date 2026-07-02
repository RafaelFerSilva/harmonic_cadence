## Why

Follow-up 2 (final) da adjudicação Chediak (`TRITONE-ADJUDICATION.md`, XXXIV pp.111-116).
Após o `fix-tritone-t-by-degree`, o ledger de trítono tem **318** ocorrências, dominadas por
classes que **o Chediak classifica com página** e o coder ainda não: **VII7** (40 em `Outro` —
"Cadencial" quando resolve no I, senão V7/III, p.112(2)); **II7** (33 em `Outro` —
"Subdominante alterada", quadro p.113); e **bVII7** (157) cuja leitura `Emp` é **condicional**
— legítima como AEM (p.112(1)), mas em tom menor um `bVII7→bIII` diatônico é **V7/III**
(dominante) e o ramo Emp o captura ANTES do teste de resolução, contradizendo o próprio
comentário do código ("a resolução precede a leitura de empréstimo"). Além disso, as leituras
não-dominantes documentadas pelo livro (bVII7/bVI7=Subd. menor, II7=Subd. alterada) seguem
poluindo o ledger como se fossem suspeitas — quando são fatos citáveis (quadro p.113).

## What Changes

- **Ordem: resolução ANTES de empréstimo.** O teste `Dsec` por resolução 4ªJ (hoje ramo 0d)
  passa a preceder o ramo Emp de bVII7/bVI7 (0c) — um `bVII7` que resolve 4ªJ acima num alvo
  diatônico (tom menor) vira `Dsec (V7/x)`, como o comentário do bloco já prometia.
- **II7 classificado**: dominante-7 na posição 2 sem casar ramo → **`SD` "Subdominante
  alterada (II7)"** (quadro p.113 + p.113(4); resolução esperada I ou I/5ª).
- **VII7 sem resolução no I classificado**: p.112(2) — sem a resolução direta no I (que já
  vira `D` cadencial hoje), o `B7` é **V7/III** → `Dsec` com alvo esperado `(V7/III)`
  (deceptivo quando nem o III vem, p.114).
- **Ledger com isenções citáveis**: as funções especiais não-dominantes DOCUMENTADAS
  (I7→`T` grau I — já isenta; IV7→`SD`; bVII7/bVI7→`Emp`; II7→`SD alterada`) saem do ledger
  com citação (quadro p.113) — no baseline (`_tritone_nondominant_ledger`) e na view
  (`v_ledger_tritone_nondominant`). O ledger residual passa a conter só o genuinamente
  não-adjudicado (bV7, resíduos).
- **Re-medição obrigatória**: gates duros 170/170 (pausa-e-investiga), ledger ~318→~25-90,
  corroboração de centro registrada.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `applied-dominant-analysis`: o requisito "Dominant-quality chords without dominant
  function" ganha (a) a precedência resolução-antes-de-empréstimo, (b) a classificação de
  II7 (Subd. alterada) e do VII7 não-resolvido (V7/III), e (c) a regra de que as funções
  especiais documentadas não são worklist (isenção citável no ledger de curadoria).

## Impact

- **Código:** `domain/harmony.py` (reordenação 0c/0d + 2 ramos novos);
  `scripts/songbook_baseline.py` e `persistence/views.sql` (isenções citáveis do ledger);
  testes novos.
- **Consumidores:** `Emp` de bVII7 em tom menor com resolução vira `Dsec` — estatísticas de
  função mudam (esperado); cadência/gates protegidos por construção (re-medidos).
- **Risco:** a reordenação muda rótulos existentes (`Emp`→`Dsec` nos casos com resolução) —
  é o único ponto não-aditivo; coberto por teste dedicado + baseline ao vivo.
