# Design — Escala-acorde dos dominantes (Chediak Vol. I, pp. 113, 121, PARTE 5)

## O bug: escala pela fundamental, cega à qualidade

`recommended_scale` mapeia `DEGREE_SCALE[posição da fundamental]`. Um `C7` em Dó
tem fundamental diatônica (I) → recebe **ionian**. Mas C7 é dominante (tem Sib);
ionian tem Si natural. A escala precisa seguir a **qualidade**, não só a posição.

## Mapa posição → escala dominante (Chediak pág. 113)

A tabela de "acordes de 7ª da dominante sem função dominante" dá a escala de cada
um. Consolidando com o dominante primário:

| Acorde | Posição | Escala (Chediak) |
| --- | --- | --- |
| V7 | 7 | mixolídio |
| I7 (blues) | 0 | mixolídio |
| IV7 (blues) | 5 | lídio b7 |
| bVII7 (subd. menor) | 10 | lídio b7 |
| II7 (subd. alt.) | 2 | lídio b7 |
| bVI7 (subd. men. alt.) | 8 | lídio b7 |
| VII7 (cadencial) | 11 | lídio b7 |
| outros (dominantes 2ºs) | — | mixolídio (padrão) |

```
_LYDIAN_DOM_POS = {2, 5, 8, 10, 11}   # II7, IV7, bVI7, bVII7, VII7
# demais posições dominantes -> mixolídio
```

## A escala lídio b7 (= nordestino)

Chediak (pág. 121) lista o modo **nordestino** `Dó Ré Mi Fá# Sol Lá Sib` — que é
o **lídio b7** (lydian dominant): `1 2 3 #4 5 6 b7`, semitons `[0,2,4,6,7,9,10]`.
Adicionado a `MODE_PATTERNS` no `cifra_core`. (O `music-theory-core` já admite
"ao menos os modos da igreja + harmônica/melódica"; escalas extras são aditivas.)

## Por que isto, e não os dominantes alterados agora

Os dominantes **alterados** (V7b9→diminuta, V7alt→alterada, V7#5→hexafônica;
Chediak P5·IV) exigem ler as tensões do parse + mais escalas — um passo maior.
Esta change resolve a lacuna estrutural (dominante → escala dominante) e a
tabela da p.113, que já temos. O alterado fica como follow-up explícito.

## Não-objetivos

- Dominantes alterados → diminuta/alterada/hexafônica (P5·IV).
- Refatorar `tensions_and_avoids` (inalterado; já opera sobre a escala dada).
