# Design — Harness de acurácia de tonalidade

## Três métricas, porque a relativa importa

A relativa maior/menor (Dó maior ≡ Lá menor — mesmas notas) é uma fonte legítima
de divergência entre fontes e detector. Medir só "tônica exata" esconde se o
detector acertou a **área tonal**. Logo:

| Métrica | Conta acerto quando... | Responde |
| --- | --- | --- |
| modo | modo detectado == anotado | acertou maior vs menor? |
| tônica exata | tônica + modo iguais | acertou exatamente? |
| relativa-consciente | exata **ou** só diferiu pela relativa | acertou a área tonal? |

`relativa-consciente ⊇ exata` sempre. A diferença entre as duas **é** o tamanho
do problema da relativa (o caso da Sina vira número).

## Parsing da anotação

O tom anotado (`Cifra.key`, ex.: `"G"`, `"Am"`, `"F#m"`, `"Bb"`): nota +
`m` opcional. Sem `m` → maior; com `m` → menor.

## Relativa

`(tônica, modo)`. Maior↔relativa menor = tônica menor 3 semitons abaixo da maior:
- anotado maior `T` / detectado menor `T-3` → relativa;
- anotado menor `T` / detectado maior `T+3` → relativa.

## Desacoplado da fonte

`evaluate_corpus(songs)` recebe `(nome, acordes, tom)` — independe de formato.
`load_corpus(dir)` lê `data/*.json` filtrando os que têm `key` (anotação). Assim
o "como medir" fica pronto e travado por teste **antes** de scrapar o "o que
medir".

## Não-objetivos

- Scraping do corpus (rede; próximo passo).
- Métrica de função/cadência (só tonalidade por ora — é a fundação).
