# Design — Cadenciais e evitados por modo (Chediak pp. 122-125)

## Dados curatoriais, não deriváveis

O campo modal é **derivável** (e já é, em `modal_field`). Mas *quais* acordes do
campo são cadenciais característicos — e quais evitar — é uma **escolha do
Chediak** (o que firma o sabor modal vs o que puxa ao tonal). Não dá pra derivar;
captura-se como dado da fonte (tétrades, pp. 122-125):

| Modo | Cadenciais | Evitar |
| --- | --- | --- |
| dórico | IIm7, IV7, bVII7M | VIm7(b5) |
| frígio | bII7M, bVIIm7 | Vm7(b5), bIII7 |
| lídio | II7, V7M, VIIm7 | #IVm7(b5) |
| mixolídio | I7, Vm7, bVII7M | IIIm7(b5) |
| eólio | IVm7, bVI7M, bVII7 | IIm7(b5) |
| iônico / lócrio | — | — |

Observações da fonte registradas como racional: o `bIII7` no frígio e o `IV7` no
dórico tendem a impor a tonalidade maior básica (por isso o cuidado/evitar); as
cadências modais só têm "sabor" em **contexto modal diatônico** (senão soam como
subdominantes menores do tonalismo) — daí o par cadencial/evitar.

## Surfacing

A seção `modal_analysis` (já populada quando há modo ativo) ganha
`characteristic_note`, `cadential_chords` e `avoid_chords` — fechando a tríade
"o que caracteriza o modo / o que firma a cadência / o que evitar".

## Não-objetivos

- Tríades cadenciais (mantemos as tétrades).
- Detectar automaticamente se a música *usa* os cadenciais/evita os evitados
  (seria uma métrica de aderência modal — passo maior).
