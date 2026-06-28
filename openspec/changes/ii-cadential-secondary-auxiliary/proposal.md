## Why

Chediak (Vol. I, XIX, p.100) define o **II cadencial**: um acorde **menor** separado do
dominante por 4ªJ ascendente (5ªJ descendente) — o `IIm` do `IIm V7→I`, "parte da cadência".
O tipo vem do **alvo do seu dominante** (o mesmo eixo da change irmã XVIII): **primário**
quando o V resolve na tônica (`Dm7 G7→C`), **secundário** quando resolve num grau diatônico
(`F#m7 B7→Em` = ii-V/iii), **auxiliar** quando resolve num acorde de empréstimo modal
(`Cm7 F7→Bb` = ii-V/bVII).

Hoje nenhum dos três é marcado como II cadencial: o primário vira `SD` (função tonal certa,
mas o papel cadencial fica invisível), e — pior — o **secundário** `F#m7` vira `Emp`
(empréstimo modal, errado: não é empréstimo, é um ii preparando um dominante) e o **auxiliar**
`Cm7` vira `T`. O código `D2` ("Segunda Cadencial") existe mas está **morto** (a função
`SD`, que lista `ii` em seus graus, é alcançada antes no laço). São erros/lacunas de função
que a API entrega.

## What Changes

- Detectar o **II cadencial** pelo par harmônico: um acorde **menor** seguido de um
  **dominante** cuja fundamental está 4ªJ acima (`interval(ii, V) == 5`).
- Classificar pelo **alvo do dominante** (`alvo = (V_root + 5) mod 12`, a 5ª justa abaixo):
  - alvo = tônica → **II cadencial primário** (`Dm7 G7→C`).
  - alvo = grau diatônico não-tônica → **II cadencial secundário** (`F#m7 B7→Em`, de V7/III).
  - alvo = empréstimo modal (não-diatônico) → **II cadencial auxiliar** (`Cm7 F7→Bb`, de V7/bVII).
- Reviver e ampliar o código `D2` para os três tipos (o nome carrega o tipo + o alvo);
  o II cadencial passa a ter precedência sobre a leitura `SD`/`Emp`/`T` desses iim7.

## Capabilities

### New Capabilities
<!-- Nenhuma: estende uma capability existente. -->

### Modified Capabilities
- `harmonic-function`: a função harmônica passa a reconhecer o II cadencial (primário,
  secundário, auxiliar) — um acorde menor que prepara um dominante — classificado pelo alvo
  do dominante, em vez de rotular o secundário/auxiliar como `Emp`/`T`.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/harmony.py` (novo ramo de II
  cadencial antes da leitura diatônica; o ramo `D2` morto da seção 2 é substituído).
  Testes em `test_applied_dominants.py`/`test_harmonic_function.py`.
- **Limitação consciente:** Chediak exige o acorde no **tempo forte**; as cifras não trazem
  metro, então o critério é a relação harmônica `iim7 → V (4ªJ acima)`. Documentado; pode
  gerar um falso-positivo raro (um iim7 que precede um dominante sem ser cadencial).
- **Não toca** `detect_key` → baseline **idêntico**. Trava: a suíte (atenção à mudança
  `Dm7 G7→C` de `SD` para `D2` — verificar testes/progressões que dependam de `SD`).
- **Dependência teórica:** classifica pelo alvo do dominante (Chediak XVIII, change irmã já
  arquivada). **Citação:** Chediak Vol. I, p.100 (XIX), lida do livro (scan).
