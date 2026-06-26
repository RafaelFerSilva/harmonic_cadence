# Design — Escalas dos dominantes alterados (Chediak P5, pp. 349-352)

## O mapa (Quadro Geral XII + preparações X/XI)

| Alteração | Escala (Chediak) | Padrão (semitons) |
| --- | --- | --- |
| b5, #11 | lídio b7 (já existe) | `[0,2,4,6,7,9,10]` |
| #5 | hexafônica (tons inteiros) | `[0,2,4,6,8,10]` (6 notas) |
| b9 | diminuta (semitom-tom) | `[0,1,3,4,6,7,9,10]` (8 notas) |
| #9 (ou b9+#9) | alterada (super-lócrio) | `[0,1,3,4,6,8,10]` |

A alteração é lida do **parse estruturado**: `b5`/`#5` no slot da quinta, `b9`/`#9`/
`#11` nas tensões. A escala alterada tem **precedência** sobre o mapa posicional
de `dominant-chord-scales` (um dominante alterado usa sua escala, não a do grau).

```
_altered_dominant_scale(chord):
    fifth augmented (#5)  → whole_tone
    fifth diminished (b5) → lydian_dominant
    #11 nas tensões       → lydian_dominant
    b9  nas tensões       → altered se também #9, senão diminished
    #9  nas tensões       → altered
    senão                 → None  (cai no mapa posicional: mixolídio/lídio b7)
```

## Spelling das escalas não-heptatônicas

`build_scale` assume uma letra por grau (7 notas). A hexafônica (6) e a diminuta
(8) violam isso: as **classes de altura ficam corretas**, mas a grafia das notas é
aproximada (pode repetir letra). Para a recomendação de escala-acorde — que usa as
classes de altura para tensões/avoids e o **nome** para exibição — isso é
suficiente. Grafia perfeita de escalas simétricas fica como refinamento.

## Não-objetivos

- Distinção por alvo (diminuta vs menor harmônica 5↓ conforme prepara maior/menor).
- `b13` isolado (mantém mixolídio — Chediak dá "mixolídio b13", escala que não
  modelamos; conservador).
- Grafia diatônica perfeita das escalas simétricas.
