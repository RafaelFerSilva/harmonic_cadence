## Why

Chediak (Vol. I, XXI–XXII, pp.102–104) classifica o acorde diminuto pela direção da
fundamental: **ascendente** (sobe ½t — resolve como dominante `V7(b9)` rootless),
**descendente** (desce ½t) e **auxiliar** (bordadura: sai e retorna ao mesmo acorde). Hoje
só o ascendente está correto (`dim7-as-dominant`). Uma sondagem ao vivo mostrou que os
outros dois tipos são **mal-classificados como "Empréstimo Modal"** (`Emp`) — uma categoria
teoricamente errada que a API entrega e o front exibiria: um `C#°7` auxiliar (bordadura
clássica do choro/bossa) ou um `Ab°7` descendente NÃO são empréstimos modais (empréstimo é
`bVI`/`bVII`/`IVm`, nunca um diminuto). Eles caem em `Emp` só porque são cromáticos
(grau não-diatônico).

A sondagem também revelou um **débito técnico**: o ramo `"Dim"` (Diminuto de Passagem) ficou
**inalcançável** — ele exige `interval_next == 1`, mas o ramo do `dim7-as-dominant` agora
intercepta exatamente esse caso e roda antes. É código morto a limpar.

## What Changes

- Classificar todo diminuto **não-dominante** (que não resolve ½t acima) por tipo, conforme
  Chediak: **auxiliar** (`prev` e `next` são o mesmo acorde — bordadura), **descendente**
  (`next` está ½t abaixo da fundamental do diminuto), e um rótulo **genérico** ("Diminuto"
  conectivo/de passagem) para o resto. Esses casos deixam de ser rotulados `Emp`.
- Preservar intactos o **ascendente → dominante** (`°7 = V7(b9)/x`, `dim7-as-dominant`) e o
  `vii°7` diatônico.
- Remover o ramo `"Dim"` morto da leitura diatônica (seção 1 de `analyze_function`),
  ofuscado pelo `dim7-as-dominant`.

## Capabilities

### New Capabilities
<!-- Nenhuma: estende uma capability existente. -->

### Modified Capabilities
- `harmonic-function`: a função harmônica passa a classificar o diminuto não-dominante por
  tipo (auxiliar/descendente/passagem) em vez de rotulá-lo como empréstimo modal.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/harmony.py` (`analyze_function`
  — ramo de classificação do diminuto não-dominante; remoção do bloco `"Dim"` morto). Testes
  em `test_harmonic_function.py` (ou novo `test_diminished_classification.py`).
- **Não toca** `detect_key` nem nada da detecção de tonalidade → as métricas do baseline
  ficam **idênticas** (mudança puramente na camada de função/rotulagem). A trava aqui é a
  **suíte de testes** (zero regressão dos rótulos corretos) + verificação ao vivo dos 3 tipos.
- **Fora do escopo (consciente):** o numeral romano de diminutos cromáticos descendentes/
  auxiliares (`roman.py`) — a mudança é sobre a **função/classificação**, não o numeral; o
  numeral mantém o tratamento atual.
- **Risco semântico nulo:** nenhum diminuto era legitimamente `Emp` (empréstimo modal é
  tríade/tétrade maior/menor de modo paralelo, nunca um diminuto), então tirá-los de `Emp`
  só corrige; nenhum teste existente prende um diminuto em `Emp`.
