## Why

A adjudicação Chediak do ledger de trítono (`TRITONE-ADJUDICATION.md`, cap. XXXIV pp.111-116)
confirmou o **maior bug residual do coder de função**: um acorde de sétima da dominante que
não casa nenhum ramo aplicado (blues, Dext, SubV, Daux, Emp, Dsec, VII7, bII7) **cai na
leitura diatônica por grau** e vira `T` pela tabela I/III/VI→T — ignorando a qualidade.
Resultado medido (n=170): **177 ocorrências** de `T` com trítono real — `VI7` (94, ex. `A7`
em Dó = V7/II), `III7` (45, `E7` = V7/VI) e `bIII7` (38). Chediak p.114(1): quando a
resolução diatônica esperada não acontece, *"trata-se de uma resolução deceptiva"* — a
análise **permanece de dominante** (notada `(V7/x)`), nunca tônica. Trítono real não é
repouso por posição; a única exceção é o I7 blues (p.112(3), já tratada e citável).

## What Changes

- **Novo ramo 0f no coder** (`HarmonicAnalysis.analyze_function`): um dominante-7 que
  atravessa todos os ramos aplicados sem casar, com raiz nos graus **VI, III ou bIII**
  (posições 9, 4, 3 semitons da tônica), é classificado **`Dsec` — dominante secundário
  resolvido deceptivamente** (Chediak p.114(1)), com o alvo esperado `(V7/x)` derivado da
  raiz (4ªJ acima). Escopo cirúrgico: **apenas** as três posições adjudicadas como bug;
  `II7`/`VII7` (função especial, p.115(4)) e `bV7` (ambíguo) ficam intactos para a change
  `classify-special-function-dominants`.
- **Re-medição obrigatória**: baseline ao vivo (3 gates duros DEVEM seguir 170/170; política
  pausa-e-investiga) + `corpus build`/`report` — o ledger de trítono deve cair ~532→~355 e a
  isenção I7 do baseline/views permanece intacta.
- Citações atualizadas onde o código menciona o veto (p.114).

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `applied-dominant-analysis`: o requisito "Dominant-quality chords without dominant
  function" ganha a cláusula de **fallback deceptivo** — um dominante-7 fora das funções
  especiais e sem resolução funcional NUNCA cai para função de repouso por grau; nos graus
  VI/III/bIII é um secundário deceptivo (`Dsec`, p.114(1)).

## Impact

- **Código:** `domain/harmony.py` (ramo 0f, ~15 linhas). Testes novos em
  `packages/harmonic_analysis/tests/`.
- **Efeito esperado no corpus:** ~177 ocorrências migram `T`→`Dsec`; funções `T` ficam mais
  honestas; estatísticas de função/bigramas mudam (esperado e desejado). HMM/cadência
  consomem `function_code` — a cadência já suprime alvo não-repouso, então `V→I` com "I"
  deceptivo deixa de ser cadência onde era falso (coerente com o gate 4).
- **Risco controlado:** o ramo só dispara APÓS todos os ramos existentes falharem (nenhum
  comportamento atual muda de rótulo, só o fall-through); gates duros re-medidos ao vivo.
