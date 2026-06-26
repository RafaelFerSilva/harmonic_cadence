# Design — Arbitragem tonalidade × modo

## O bug-fundação (sinalizado no dia 1)

Na exploração inicial, a Tensão #3 foi: *"`detect_mode` sobrescreve `detect_key`
silenciosamente; quando discordam, o modo ganha — fonte de incoerência que
cascateia por todo o relatório."* Construímos a teoria toda **em cima** dessa
fundação sem consertá-la. A Sina (Lá maior → "Ré menor") foi a prova real.

## Por que NÃO unificar na tônica do detect_key

A ideia óbvia — "detect_key é dono da tônica, detect_mode só do modo" — falha:
o K-S **não acerta a tônica modal**. Verificado: `G F C G` (Sol mixolídio) → o
detect_key diz **Dó maior** (o pai), não Sol. Unificar perderia os modos genuínos.

## A regra que cai do quadro: refinar, nunca inverter

Comparando os dois detectores no corpus:

| Música | detect_key | detect_mode | decisão |
| --- | --- | --- | --- |
| Wave | D maior | D frígio (menor) | qualidade discorda → **rejeita** → D maior |
| Oceano | D maior | A frígio | tônica discorda → **rejeita** → D maior |
| Sozinho | B menor | B mixolídio (maior) | qualidade discorda → **rejeita** → B menor |
| Papel Marché | A menor | A frígio (menor) | ambas concordam → **aceita** → A frígio |
| Sina | A maior | None (após bass-fix) | — → A maior |

**Um modo só refina a tonalidade quando concorda na tônica E na qualidade.** Se
inverte a qualidade (maior↔menor) ou muda a tônica, é cromatismo tonal — e o
`detect_key` (confiável em maior/menor) prevalece. Para modos genuínos (mixolídio
sobre tom maior, frígio sobre tom menor) a qualidade concorda → aceitos.

## Centro tonal = baixo predominante

`detect_mode` usava a raiz do **último acorde** — frágil (Sina: `D/A` → Ré). O
centro passa a ser o **baixo mais frequente** (o pedal/finalis), com bônus para
o primeiro e o último acorde. O baixo é o ancoradouro tonal; para a Sina, Lá
domina o baixo (pedal) e vence Ré com folga.

## Coerência a jusante

Quando a arbitragem rejeita, **anula-se o `mode_info`** — assim o override de
tonalidade *e* a seção `modal_analysis` (populada separadamente) ficam coerentes:
nada de "tom Ré maior" com "modal: Ré frígio" ao mesmo tempo.

## Limitação registrada

Se o `detect_key` erra a tônica de um modo menor genuíno (pega o relativo maior),
a arbitragem rejeita o modo (qualidade discorda) e fica no tom errado. Resolver
isso exige melhorar a detecção de centro tonal modal — passo maior.
