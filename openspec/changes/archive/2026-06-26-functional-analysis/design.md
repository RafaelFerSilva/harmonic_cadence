# Design — Função harmônica (fonte: Chediak Vol. I, pp. 91–96, 111–113)

## Protocolo

Cada decisão abaixo é traçada em paralelo com Chediak (página citada). Onde ele
silencia ou diverge do corpus, registra-se *"sem fonte"* + divergência. Ver
[[chediak-as-decision-arbiter]].

## 1. As três funções (pág. 91)

Chediak: *"São três as funções harmônicas: tônica (estável), dominante
(instável) e subdominante (menos instável)."*

- **Tônica** — repouso/conclusão; principal **I**, substitutos **VI** e **III**.
- **Dominante** — tensão, pede resolução; principal **V**, substituto **VII**.
- **Subdominante** — meio-suspensiva, intermediária; principal **IV**, substituto **II**.

**Paralelo:** confere com `constants.HARMONIC_FUNCTIONS` (T: I/III/VI · SD: II/IV
· D: V/VII). Estávamos certos — esta change só formaliza.

## 2. Qualidade funcional — forte/meio-forte/fraco (pág. 92) — NOVO

| Função | Forte | Meio-forte | Fraco |
| --- | --- | --- | --- |
| Tônica | I | — | VI, III |
| Dominante | V | VII | — |
| Subdominante | IV | II | — |

Princípio: função **principal** (I, IV, V) = forte; **substitutos do IV e V**
(II, VII) = meio-forte; **substitutos do I** (III, VI) = fraco. Não modelamos
isso hoje — é um peso de confiança por grau, que pode qualificar o rótulo e, no
futuro, alimentar a emissão do HMM (`probabilistic-functional-parsing`).

## 3. Quadro função × grau, quatro escalas (pág. 96)

Função **por posição de grau** (I→T, II→SD, III→T, IV→SD, V→D, VI→T, VII→D):

| Escala | I (T) | II (SD) | III (T) | IV (SD) | V (D) | VI (T) | VII (D) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Maior | I7M | IIm7 | IIIm7 | IV7M | V7 | VIm7 | VIIm7(b5) |
| Menor harmônica | Im(7M) | IIm7(b5) | bIII7M(#5) | IVm7 | V7 | bVI7M | VII° |
| Menor natural | Im7 | IIm7(b5) | bIII7M | IVm7 | *Vm7 | bVI7M | bVII7 |
| Menor melódica | Im(7M) | IIm7 | bIII7M(#5) | **IV7 | V7 | VIm7(b5) | VIIm7(b5) |

`*` `Vm7` (menor natural) = **não tem função tonal** (sem sensível).
`**` `IV7` (menor melódica) = subdominante com sétima (IV grau blues).

**Paralelo:** nosso campo menor é único (`DEGREES_MINOR`). Chediak o abre em três
escalas — um acorde é **diatônico à menor** se aparece em *qualquer* das três
(harmônica ∪ natural ∪ melódica real). E o `Vm7` natural sai da função dominante.

> Nota: a função é **posicional** aqui (baseline). O refinamento contextual de
> dom7 (seção 4) sobrepõe casos como `bVII7`, que pela posição cairia em "D" mas
> **funciona como subdominante menor** (pág. 112).

## 4. Dom7 sem função dominante (pp. 111–113) — CORREÇÃO DE BUG

Chediak: *"Quando o acorde de 7ª da dominante não resolve de modo regular
(V7→I ou SubV7→I), o contexto define a análise."* Três classes; aqui a (a),
que é a que mais corrige nosso código:

**Acordes de função especial, não dominante (Quadro pág. 113, tom de Dó):**

| Acorde | Grau | Função | Escala |
| --- | --- | --- | --- |
| Bb7 | bVII7 | Subdominante menor (AEM no maior) | Lídio b7 |
| C7 | I7 | Blues | Blues, mixolídio |
| F7 | IV7 | Blues | Blues lídio b7 |
| B7 | VII7 | Cadencial (ou V7/III deceptivo) | Lídio b7, mixolídio |
| D7 | II7 | Subdominante alterado | Lídio b7, mixolídio |
| Ab7 | bVI7 | Subdominante menor alterado | Lídio b7 |

Regras de contexto (Chediak):
- `bVII7` resolve por baixo um **tom acima** (`Bb7→C`); às vezes substitui o `IVm`.
- `VII7` é **cadencial** quando resolve direto no I com duração longa e sem `II`
  cadencial antes; é `V7/III` quando curto ou no clichê `IIIm … V7`.
- `I7`/`IV7` são **blues** (IV7 também pode ser `V7/bVII` ou `SubV7/IIIm`).
- `II7`/`bVI7` relacionam-se pelo trítono (como `#IVm7(b5)`) → subdominante alterado.

**Paralelo:** hoje `analyze_function` vê `chord.is_dominant_seventh` + resolução
de 5ª e marca `Dsec`. A correção: **antes** de marcar dominante secundário,
testar se o acorde é um desses casos especiais (pela posição de grau + contexto),
e só então cair em `Dsec`/`SubV`. Isso mora em `applied-dominant-analysis`.

## Non-goals

- Cadências (pp. 109–111), modulação (116–119), sinalização analítica (100–102):
  temas/changes separados.
- A emissão probabilística do HMM: a qualidade funcional **pode** alimentá-la,
  mas isso é follow-up, não esta change.
- `°` = dim7, dialetos `±`: já resolvidos na change `chord-parsing`.
