## Why

A classificação de função harmônica (T/SD/D) é o coração de `harmony.py`, mas
tem dois problemas e uma lacuna de spec — todos endereçáveis pela fonte
(Chediak Vol. I, pp. 91–96 e 111–113):

- **Bug (over-labeling de dominante secundário):** `analyze_function` rotula
  *qualquer* acorde de 7ª da dominante que resolva uma 5ª abaixo num não-tônica
  como dominante secundário (`Dsec`). Chediak (pp. 111–113) documenta acordes de
  7ª da dominante **sem função dominante**: `bVII7` (subdominante menor), `I7`/
  `IV7` (blues), `VII7` (cadencial), `II7`/`bVI7` (subdominante alterado). Hoje
  esses são mal-rotulados.
- **Lacuna de campo menor:** `constants.DEGREES_MINOR`/`MODE_HARMONY` usam um
  campo menor único. Chediak (pp. 94–96) usa **três escalas** (harmônica, natural,
  melódica real) e marca o `Vm7` da menor natural como **sem função tonal** (sem
  sensível, não é dominante).
- **Lacuna de spec:** a classificação diatônica T/SD/D não tem capability própria
  (vive implícita em `HARMONIC_FUNCTIONS`). Chediak (p. 92) ainda dá uma
  **qualidade funcional** — forte/meio-forte/fraco — que não modelamos e que
  qualifica a confiança de cada rótulo.

O esqueleto diatônico atual (I/III/VI→T, II/IV→SD, V/VII→D) **confere** com
Chediak (pp. 91, 96) — esta change formaliza isso e corrige o resto.

## What Changes

- **Nova capability `harmonic-function`:** classificação diatônica T/SD/D por
  grau (p. 96), a **qualidade funcional** forte/meio-forte/fraco (p. 92), e o
  **campo diatônico menor sobre três escalas** com o `Vm7` natural sem função
  tonal (pp. 94–96).
- **Modificar `applied-dominant-analysis`:** quando um acorde de 7ª da dominante
  **não** resolve `V7→I` nem `SubV7→I`, classificá-lo pela função especial
  (subdominante menor / blues / cadencial / subdominante alterado), em vez de
  forçar dominante secundário.
- Cada decisão cita a página do Chediak (protocolo de paralelo com a fonte).

Fora de escopo (temas/changes separados): cadências (pp. 109–111), modulação
(pp. 116–119), sinalização analítica/cifra romana de saída (pp. 100–102), e a
ponte probabilística (`probabilistic-functional-parsing` já é capability — a
qualidade funcional pode alimentá-la depois).

## Capabilities

### New Capabilities
- `harmonic-function`: classificação diatônica de função (T/SD/D), qualidade
  funcional (forte/meio-forte/fraco) e campo diatônico menor de três escalas.

### Modified Capabilities
- `applied-dominant-analysis`: acordes de 7ª da dominante **sem** função
  dominante são classificados por função especial em vez de dominante secundário.

## Impact

- **`harmonic_analysis/domain/constants.py`**: `HARMONIC_FUNCTIONS` confirmado
  (I/III/VI, II/IV, V/VII); ganha qualidade funcional e o campo menor de três
  escalas.
- **`harmonic_analysis/domain/harmony.py`**: `analyze_function` ganha o ramo de
  dom7-sem-função; o `Vm7` da menor natural deixa de ser tratado como dominante.
- **Testes**: acordes do corpus como oráculo (`Bb7` como `bVII7`/subd. menor em
  Dó; `C7`/`F7` como blues; `B7` como `VII7` cadencial vs `V7/III`).
