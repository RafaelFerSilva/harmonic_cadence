# Roadmap

Princípio: **fundação antes de produto, e medível antes de "achismo"** (a lição da
análise da Sina — um erro de tom que só foi pego a olho humano).

A teoria do Chediak (Vol. I) está destilada, implementada e testada. A fronteira
agora é **confiança/precisão** e **apresentação** para o público BR.

## Espinha (sequencial, orientada a dado)

- **Fase A — Medição.** Corpus anotado (~30–40 músicas com tom/modo de
  referência) + harness de acurácia → um número de baseline. Destrava todo o
  resto: regressões pegas automaticamente, base pra calibrar de verdade.
  *(Gargalo: anotação dos tons corretos — onde a expertise de harmonia vale.)*
- **Fase B — Centro tonal.** Alvo afiado pelo baseline (`scripts/key_baseline.py`,
  vs ouro Chediak, n=6: modo 67% · exata 33% · relativa-consciente 67%): a
  fraqueza sistemática é a **confusão maior ↔ relativa menor** (perfis K-S
  parecidos) — desambiguar com acorde final / cadência / primeiro acorde, não só
  o histograma. Secundário: o K-S não acha a tônica de modos. Medido contra o
  baseline. **Depende de A.**

## Trilha paralela (contida, baixo risco, encaixa cedo)

- **Localização PT-BR.** Toda saída em português consistente (`Ré menor`,
  `frígio`, `dominante`, `mixolídio`). Decisão: modelo interno em inglês canônico;
  tradução na fronteira de apresentação (padrão i18n). Não toca algoritmo.
- **Observabilidade.** `logging` + campo `diagnostics` (quais seções degradaram)
  no lugar do `try/except` mudo + `print`. Distingue "nada se aplica" de
  "estourou"; torna a Fase A honesta.
- **Spelling enarmônico.** Rotear `describe_modal_borrowing`/`transpose` pela
  `Note` soletrada (fim do `A#` onde é `Bb`). Correção pedagógica (Tensão #2 do
  dia 1, ainda aberta).
- **Consolidação legada.** Unificar `MODE_HARMONY` → `modal_field` derivado;
  aposentar o `normalize_note` sustenido-só. Mata duas-fontes-de-verdade.

## Sequência recomendada

| # | Tema | Change | Tam. |
|---|---|---|---|
| 1 | Localização PT-BR | `pt-br-localization` | S–M |
| 2 | Observabilidade | `pipeline-observability` | S–M |
| 3 | Fase A: corpus + harness | `validation-corpus` | M |
| 4 | Spelling enarmônico | `enharmonic-spelling` | S–M |
| 5 | Fase B: centro tonal | `tonal-center-detection` | L |
| 6 | Consolidação legada | `consolidate-modal-field` | S |

Localização e Spelling juntas fecham a **correção de apresentação** (PT correto +
grafia enarmônica) — o que torna a ferramenta pedagógica de verdade para o BR. A
espinha de precisão (Observabilidade → Corpus → Centro tonal) segue logo atrás.
