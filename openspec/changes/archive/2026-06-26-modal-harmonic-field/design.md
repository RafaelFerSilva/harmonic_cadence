# Design — Campo harmônico modal (fonte: Chediak Vol. I, pp. 120-125)

## Derivar, não transcrever

`MODE_HARMONY` foi transcrito à mão e tem erros (frígio/lídio/mixolídio). Em vez
de só corrigir os números, a fonte de verdade passa a ser **derivada**: empilha
terças sobre cada grau da escala modal (`build_scale`, que já soletra certo os 7
modos) e classifica a tétrade pelos intervalos. Correto por construção; imune a
erro de transcrição. As tabelas do Chediak viram **testes** (o oráculo).

## Campo (tétrades) por modo — Chediak pp. 122-125

| Modo | I | II | III | IV | V | VI | VII |
| --- | --- | --- | --- | --- | --- | --- | --- |
| iônico | I7M | IIm7 | IIIm7 | IV7M | V7 | VIm7 | VIIm7(b5) |
| dórico | Im7 | IIm7 | bIII7M | IV7 | Vm7 | VIm7(b5) | bVII7M |
| frígio | Im7 | bII7M | bIII7 | IVm7 | Vm7(b5) | bVI7M | bVIIm7 |
| lídio | I7M | II7 | IIIm7 | #IVm7(b5) | V7M | VIm7 | VIIm7 |
| mixolídio | I7 | IIm7 | IIIm7(b5) | IV7M | Vm7 | VIm7 | bVII7M |
| eólio | Im7 | IIm7(b5) | bIII7M | IVm7 | Vm7 | bVI7M | bVII7 |
| lócrio | Im7(b5) | bII7M | bIIIm7 | IVm7 | bV7M | bVI7 | bVIIm7 |

> Erratum da fonte: na tabela do frígio, o IV impresso aparece como `A7`, mas o
> próprio livro lista a tríade como `IVm` (Am) e a teoria dá `Am7`. Seguimos a
> derivação (`m7`), que é coerente com a tríade e com a escala.

## Nota característica por modo (Chediak)

```
dórico b → 6 (6ª maior)   frígio → b2   lídio → #4
mixolídio → b7   eólio → b6   lócrio → b2 e b6   iônico → (nenhuma)
```

## Princípio modal (pág. 121)

Chediak: *"A característica básica da harmonia modal é a não resolução do trítono
com expectativa."* É o que separa o modal do tonal — registrado aqui como
racional; sua operacionalização (detectar não-resolução) fica para depois.

## Não-objetivos

- Acordes cadenciais/evitados por modo (Chediak os dá; próximo passo).
- Modalismo puro vs misto (pág. 121); pentatônicas; modos sintéticos.
- Refatorar `describe_modal_borrowing` para consumir `modal_field` (a correção
  de `MODE_HARMONY` já o deixa correto; a unificação fica para depois).
