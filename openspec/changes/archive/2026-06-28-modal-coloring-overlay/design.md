## Context

O sistema é tonal-funcional por padrão. A análise funcional (`harmony.py`) já rotula
empréstimo modal por acorde — bVII7 → `"Emp"` (subdominante menor, Chediak),
`describe_modal_borrowing` nomeia a origem — e `constants.py` reconhece progressões
modais. O que falta é o **resumo no nível da peça**: afirmar "esta peça tonal tem
coloração mixolídia" quando os empréstimos formam um padrão.

O detector de modo automático foi removido (`fix-or-remove-church-mode`) porque
re-centrava sobre a coleção cromática e substituía o eixo (frígio falso em 53/60). Esta
change reintroduz o modalismo pela via oposta: um overlay descritivo que **não re-centra
e não substitui nada**.

## Goals / Non-Goals

**Goals:**
- Resumir, no nível da peça, os empréstimos modais já detectados num rótulo de coloração.
- Ancorar tudo na tônica do `detect_key`; jamais re-estimar um centro.
- Ser estritamente aditivo e omissível; risco zero sobre tom/grau/função/cadência.

**Non-Goals:**
- Reintroduzir detecção automática de **centro** modal (3b, bloqueado).
- Reescrever graus/funções como modais, ou competir com o eixo tonal.
- Cobrir mais que mixolídio (sobre maior) e frígio (sobre menor) na v1. Dórico, lídio b7
  e os demais ficam para depois — dórico especificamente depende do 3b (centro modal).

## Decisions

### D1 — A evidência é a sequência de graus TONAIS, ancorada na tônica do `detect_key`

A regra lê a sequência de graus que a análise tonal já produz (numerais relativos à
tônica tonal), não uma coleção de alturas nem um centro re-estimado. Isso mata o bug
histórico por construção: "Mi menor" nunca vira "Mi frígio" por acaso — só há coloração
frígia se o **bII aparecer como acorde** relativo ao Mi já fixado.

```
detect_key → A menor (tônica = A, fixa)
graus:  i  bII  i  v        ← bII = Bb maior, acorde real
        └─ bII→i presente → coloração FRÍGIA (evidência: cadência bII→i)
tom/modo/função: INTOCADOS (segue A menor, funções tonais)
```

### D2 — Gatilho ASSIMÉTRICO, calibrado contra dados e ancorado em Chediak

A curadoria do ground-truth (sondagem ao vivo + Chediak pp. 122-127) **refutou** a regra
simétrica inicial e fixou v1 em **dois modos** com gatilhos distintos:

| Modo (sobre) | Sinais (não-diatônicos ao tom) | Gatilho |
|---|---|---|
| mixolídio (MAIOR) | bVII maior; **v menor** (Vm) | bVII→I (≥1) **OU** bVII distinto ≥2 **OU** Vm distinto ≥2 |
| frígio (MENOR) | bII maior | **bII→i estrutural ≥2** |

Justificativas (cada uma veio do dado, não de chute):
- **Mixolídio só sobre MAIOR.** No menor, o bVII é diatônico (eólio) — a regra simétrica
  disparava "mixolídio" em toda música menor. Chediak confirma: cadências eólias
  "seriam apenas subdominantes menores de uso corrente na harmonia tonal" (p. 124).
- **Vm como 2º sinal mixolídio.** Chediak dá I7/Vm7/bVII7M como cadenciais do mixolídio
  (p. 124). **Upa Neguinho** (Ré mixolídio, p. 126) é mixolídio por **Vm7=Am7, sem
  bVII** — só-bVII a perderia. O v menor é não-diatônico ao maior (inequívoco).
- **Frígio exige a cadência bII→i estrutural (≥2), não recorrência.** Um bII maior no
  menor quase sempre é **napolitano/SubV** (função tonal — que o sistema já rotula
  "SubV"). Sem o ≥2, os controles eólios (Corcovado, Insensatez, Construção) disparavam
  falso; com ele, só Canto de Ossanha (bII→i ×22) sobrevive.
- **Dórico fica FORA da v1.** O sinal "IV maior" dispara em eólias com dominantes
  secundários (Wave: IV maior ×39). Pior: dórico↔mixolídio compartilham coleção
  (Arrastão = Lá dórico p. 125, mas detect_key ancora em Ré maior e lê superfície
  mixolídia) — separá-los exige **detecção de centro modal (3b, bloqueado)**.

Reusa `MODAL_CADENCE`/`characteristic_degree` da biblioteca preservada; ancora sempre na
tônica tonal (D1).

### D3 — Saída: campo estruturado + linha descritiva, omitida por padrão

```python
modal_coloring = {
  "flavor": "mixolydian",                 # mixolydian | phrygian | dorian
  "evidence": ["cadência bVII→I (compassos 7-8)", "bVII recorrente (2×)"],
  "where": [indices ou trechos],
}  # ou None — o caso comum
```

Render PT-BR: "Coloração modal: traços mixolídios (bVII→I)". Seção subordinada à tonal,
omitida quando `None` (como `analysis-reporting` já faz para seções ausentes).

### D4 — Relação com "Emp": resumo, não substituição

O rótulo "Emp" por acorde permanece intocado (é a verdade tonal-funcional: um
empréstimo). `modal_coloring` é a **agregação** desses empréstimos quando consistentes.
Um bVII isolado segue só "Emp", sem coloração; dois bVII ou um bVII→I viram "Emp" **e**
coloração mixolídia. Camadas independentes, sem conflito.

### D5 — Ground-truth ancorado em Chediak; divergências documentadas

O corpus de validação (`scripts/modal_coloring_groundtruth.py`) é ancorado nas
classificações do próprio Chediak (pp. 125-127), não em hipóteses: Arrastão (dórico),
Upa Neguinho + Procissão (mixolídio), Cravo e Canela (iônico), Pra Não Dizer (eólio),
Gravidade (lídio b7), mais positivos verificados por dado (Ponteio mixo; Canto de Ossanha
frígio) e controles negativos eólios (Wave, Corcovado, Insensatez, Construção).

Testes deterministicos offline usam progressões sintéticas por modo; o corpus de fatos
serve à validação ao vivo (rede), como o `key_baseline`. A disciplina do projeto: nunca
afirmar modo sem evidência verificada, e **registrar divergência** quando o detector e
Chediak discordam (D6).

### D6 — O detector lê HARMONIA, não melodia: três classes de divergência vs Chediak

A coloração é, por construção, **superfície harmônica relativa ao centro tonal** — uma
aproximação de Chediak, não sua reprodução. O compositor brasileiro frequentemente veste
melodia modal com harmonia tonal, então divergências são esperadas e **documentadas, não
escondidas**:

1. **Divergência de arranjo** — Procissão é Dó mixolídio com Bb→C em Chediak, mas a cifra
   raspada veio tonalizada (sem Bb) → silêncio fiel ao arranjo. O detector está certo
   sobre a cifra que vê.
2. **Divergência de centro** — Arrastão é Lá dórico, mas detect_key ancora em Ré maior →
   superfície mixolídia. Resolver exige centro modal (3b). v1 não mira dórico.
3. **Cobertura de sinal** — mitigada ao adicionar Vm como sinal mixolídio (catch Upa
   Neguinho); o que sobrar (ex.: lídio b7 de Gravidade) fica fora da v1, explícito.

## Risks / Trade-offs

- **Risco: reintroduzir o falso-positivo.** Mitigação tripla: ancoragem na tônica tonal
  (sem re-centragem), evidência de acordes reais (não coleção cromática), e o teste de
  silêncio nas eólias como trava de regressão.
- **Trade-off: cobertura parcial (3 modos).** Aceito: mixolídio/frígio/dórico cobrem a
  esmagadora maioria da coloração modal da MPB; lídio/locrian/etc. são raros e ficam para
  uma extensão se a evidência aparecer.
- **Risco: confusão com a seção modal antiga.** Não há: a antiga foi removida. A nova é
  explicitamente "coloração" (overlay), não "Centro modal" (eixo) — nomenclatura distinta
  no relatório.
- **Subjetividade da fronteira.** Onde "empréstimo pontual" vira "coloração" é uma
  escolha (≥2 / cadência). Documentada e recalibrável contra o ground-truth, não fixada
  por chute.
