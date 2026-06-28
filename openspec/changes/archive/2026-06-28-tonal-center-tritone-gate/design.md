## Context

`detect_key` faz K-S → desempate cadencial **dentro** da `TIE_BAND` (Fase B v1) → correção
de modo paralelo. O `cadence_corroboration` premia 1º/último acorde e uma "cadência
autêntica" identificada só pela **fundamental em V** (`tonic+7`), sem checar o trítono. Os
5 erros de centro verificados são **V-detectado-como-tônica**: a tônica verdadeira está
fora da banda e o K-S prefere o V. O parser já tipa o trítono (`Category.DOMINANT`,
chord_parse p.84) e já é posicional (1º, último, janela final) — a fundação existe.

## Goals / Non-Goals

**Goals:**
- Corrigir o **centro tonal** (V detectado como tônica) escapando da banda só com certeza
  **funcional** (qualidade do acorde), sem regredir as ~41 corretas nem as 4 métricas.

**Non-Goals:**
- **Arbitragem modal de centro** (Arrastão→Lá) e **métrica degree-relative** — change
  própria (`modal-center-arbitration`).
- dim7-como-dominante (coringa de 2 trítonos) — change própria.
- Tocar `segment_keys`/modulação ou reescrever o K-S.

## Decisions

### D0 — Duas abordagens reprovadas pela trava antes da que venceu (registro honesto)

Os "4 filtros" (proposta original do time) e o finalis-only foram implementados e
**reprovados pelo baseline ao vivo**:

```
  v1  recorrência + trítono-coleção   exata 67→36%   catástrofe (disparou em secundários)
  v2  finalis-only (coleção-fit)      exata 67% mas  0 alvos fixos + modo 86→83%
  v3  GATE DE QUALIDADE               exata 67→69 · relativa 74→76 · centro 74→79 · 0 regressão
```

Causa-raiz dos fracassos: a **densidade de dominantes secundários da MPB** derrota todo
discriminador local de coleção/trítono — o V7/V injeta a nota cromática que faz a coleção
do palpite errado casar tão bem quanto a certa. O discriminador que funciona não é
estatístico, é **funcional**: a qualidade do acorde.

### D1 — Gate de QUALIDADE: a tônica repousa, o V é tensão

K-S manda dentro da banda (Fase B v1 intacta). O gate corrige o centro `Y` → `X` só com
certeza funcional inequívoca:

```
1. Y aparece SÓ como dominante-7   (todo acorde em Y é Category.DOMINANT; se Y repousa
                                    uma vez como maj7/6/m7/tríade → É tônica → não mexe)
2. Y7 resolve uma 5ª abaixo        (baixo seguinte cai em X = (Y−7) mod 12)
3. X é REPOUSO                     (X aparece como Category.MAJOR/MINOR — ponto de descanso)
```

Robusto a secundários: o sinal é a **saúde do repouso da peça inteira**, não notas
isoladas. Em Garota, Dó é sempre Dó7 (tensão) e resolve em Fámaj7 (repouso) → corrige
Dó→Fá. Ultraconservador: nas 41 corretas a tônica aparece como repouso → o gate retorna
None na hora.

### D2 — Guard do blues/mixolídio (Chediak p.121)

A pergunta do "I7 constante de blues": se `Y` nunca repousa MAS o alvo `X` também só
aparece como dominante (tudo é tensão — `C7-F7-G7`), o gate **aborta**. O trítono do I7 de
blues **não resolve com expectativa** (Chediak p.121) → não é dominante funcional. Sem
ponto de repouso, o gate não age; o caráter mixolídio/blues fica para a coloração (3b-cor).

### D3 — dim7 inelegível

O gate só considera `Category.DOMINANT` (1 trítono). O °7 (2 trítonos, 4 resoluções) nunca
entra. Modelar o viio7 como dominante de 1ª classe é change própria.

### D4 — A trava é inegociável

O baseline ao vivo é o juiz: as 4 métricas Cifra-Club não podem regredir; o `center_accuracy`
tem que subir. Validado: modo/coleção idênticos (86/97), exata 67→69, relativa 74→76, centro
74→79 (Garota corrigida). Só 1 dos 5 alvos foi corrigido **de propósito** — o gate segura
nos 4 onde o sinal de qualidade não é limpo (consertar o certo, não chutar o resto).

### D5 — Arbitragem modal e métrica degree-relative: ADIADAS

A metade modal do 3b (Arrastão→Lá, ausência de dominante + cadência modal → finalis) e a
métrica de centro modal degree-relative são **novas frentes de integração** — vão para uma
change própria (`modal-center-arbitration`), para não arriscar o ganho tonal já validado.
A lei degree-relative (`center-eval-degree-relative`) fica registrada para ela.

## Risks / Trade-offs

- **Risco principal (regredir as 41) — mitigado e validado.** O gate só dispara quando o
  centro do K-S é inequivocamente um V (aparece só como dominante); nas peças certas a
  tônica repousa → None. A trava ao vivo confirmou zero regressão.
- **Cobertura parcial (1 de 5):** aceito por design — o gate é conservador. Afrouxar para
  pegar A Banda/Aquele Abraço/etc. arrisca as 41 (já vimos 2× o preço); fica para iteração
  guiada por dado, não agora.
- **Trade-off do guard de blues:** uma peça tonal genuína cujo I e V só aparecem como 7
  (raro fora do blues) não seria corrigida. Aceito — o silêncio é seguro.
