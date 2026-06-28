## Why

Chediak (Vol. I, XVIII, p.99) distingue a preparação dos graus não-tônica por dois eixos.
**O alvo** decide o nome: dominante **secundário** prepara um grau **diatônico** (V7/ii,
V7/V…); dominante **auxiliar** prepara um acorde de **empréstimo modal** (V7/bIII, V7/bVI…)
— ambos por 5ª justa descendente do baixo. **O movimento** decide a outra família: o
**SubV7 secundário** prepara um grau diatônico resolvendo ½t descendente (Ab7→G = SubV7/V).

Hoje o analisador só tem o dominante secundário e o SubV **primário** (da tônica). Uma
sondagem ao vivo confirmou os buracos: `Bb7→Eb` (dominante auxiliar V7/bIII) é rotulado
"Empréstimo Modal bVII7"; `Eb7→Ab` (auxiliar V7/bVI) vira `V7/None`; `Ab7→G` (SubV7/V) vira
"Empréstimo bVI7"; `Eb7→Dm` (SubV7/ii) vira "Emp". São erros de função que a API entrega e
o front exibiria.

## What Changes

- Detectar o **dominante auxiliar**: um dom7 que resolve **5ª justa descendente** num alvo
  de **empréstimo modal** (não-diatônico, não-tônica) → função dominante, rótulo
  `Dominante auxiliar (V7/<grau cromático>)` (Chediak XVIII-b, p.99). Novo código `Daux`.
- Detectar o **SubV7 secundário**: um dom7 cuja fundamental está **½t acima** de um alvo
  **diatônico não-tônica** (resolve ½t descendente) → `SubV7 secundário (SubV7/<grau>)`
  (Chediak XVIII-c, p.99). Reusa o código `SubV`.
- **Reordenar** o ramo de dominante para a resolução funcional preceder a leitura de
  `bVII7`/`bVI7` como empréstimo (`Bb7`/`Ab7` que **resolvem** deixam de ser `Emp`), **sem**
  tocar o I7/IV7 blues (Chediak XXXIV os fixa como blues) nem o `bVII7→I`/`bVI7` que **não**
  resolvem (seguem `Emp`).

## Capabilities

### New Capabilities
<!-- Nenhuma: estende uma capability existente. -->

### Modified Capabilities
- `applied-dominant-analysis`: adiciona o dominante auxiliar (alvo de empréstimo modal) e o
  SubV7 secundário (alvo diatônico), distinguindo-os do dominante secundário e do SubV
  primário pela natureza do alvo e pelo movimento do baixo.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/harmony.py` (reorganização do
  ramo `if chord.is_dominant_seventh:`); `constants.py` (novo `Daux` em
  `HARMONIC_FUNCTIONS` + `FunctionCode`). Testes em `test_applied_dominants.py`.
- **Não toca** `detect_key` → baseline **idêntico** (mudança na camada de função). Trava: a
  suíte de testes (preservar V7/x secundário, SubV primário, I7/IV7 blues, bVII7/bVI7→Emp
  sem resolução) + verificação ao vivo dos casos novos.
- **Fora do escopo (próxima change):** II cadencial secundário/auxiliar (Chediak XIX) — o
  iim7 que prepara estes dominantes; e dominantes/II-V's estendidos (XXVIII).
- **Citação:** Chediak Vol. I, p.99 (XVIII), lida do livro (scan), destilada como fato.
