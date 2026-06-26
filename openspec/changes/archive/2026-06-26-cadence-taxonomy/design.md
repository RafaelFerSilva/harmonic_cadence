# Design — Taxonomia de cadências (Chediak Vol. I, pp. 109-111)

## As cinco cadências (Chediak XXXII)

| Cadência | Definição (Chediak) | Detecção |
| --- | --- | --- |
| perfeita | V→I, **estado fundamental** | a=V, b=I, sem inversão |
| imperfeita | V→I com **inversão**, ou **VII→I** | V→I com baixo ≠ fundamental, ou VII→I |
| plagal | **IV→I ou IIm→I** (S→T) | a∈{IV,II}, b=I |
| meia-cadência | qualquer grau → **V** | b=V, a≠V |
| deceptiva | V → **qualquer não-tônica** | a=V, b≠I |

Mais a **autêntica** (Chediak a): a perfeita *precedida de subdominante*
(IV ou II → V → I) — detectada por janela de 3 acordes.

## Como decidir perfeita vs imperfeita

Chediak: a imperfeita é V→I "onde um ou ambos os acordes estão **invertidos**, ou
ainda no caso VII→I". A inversão é lida do **baixo cifrado** (`C/E` → baixo E ≠
fundamental C). O parser de acorde já expõe `properties.bass`; basta comparar com
a fundamental. Sem informação de soprano, a distinção perfeita/imperfeita por
*voicing melódico* (3ª/5ª no soprano) fica fora — usamos a inversão do baixo, que
é o critério decidível e o que a cifra estabelece.

## Grau, não tom

A classificação usa `degree_base` (numeral romano de posição, ignora acidente e
qualidade) — então funciona igual em maior e menor (tônica `I`/`i` → `I`;
dominante `V`/`v` → `V`). O parâmetro `mode` torna-se redundante mas é mantido na
assinatura por compatibilidade com os chamadores.

## Não-objetivos

- Deceptiva **modulante** (V→novo tom): precisa de detecção de modulação.
- Perfeita/imperfeita por nota de soprano (a cifra não estabelece o soprano).
