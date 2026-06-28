## Why

A detecção de tonalidade ainda erra o **centro** entre graus diatônicos. A change
`chediak-structural-gold` mediu o buraco: **74% (14/19 verificados)**, com 5 casos de
**V-detectado-como-tônica** — Garota de Ipanema (F→C), A Banda (D→A), Aquele Abraço (E→A),
Apesar de Você (D→A), Menino do Rio (F→C). O K-S "morde a isca": as notas do V (ou da
mediante) são um subconjunto resistente da tônica, então o histograma é enganado e a
tônica verdadeira cai **fora** da `TIE_BAND`. A Fase B v1 (`cadence_corroboration`) só age
**dentro** da banda e aceita qualquer acorde com fundamental em V — não checa o trítono.

Chediak dá o critério que falta (p.121): *"a característica básica da harmonia modal é a
não resolução do trítono com expectativa"* — e o exemplo (Dm7 é IIm7 em Dó, mas função
tônica em Ré dórico) prova que o que **define o centro** é a resolução do trítono do
dominante funcional. É a fundação mecânica do tonalismo, forte o bastante para tratorar o
palpite estatístico — desde que peneirada com rigor para não estragar as ~41 corretas.

## What Changes

- **Gate de QUALIDADE (escapa a `TIE_BAND`):** o discriminador não é a coleção nem o
  trítono isolado (ambos reprovados na validação — ver design), é a **qualidade funcional
  do acorde** (Chediak): a tônica é **repouso** (aparece como maj7/6/m7/tríade); o V é
  **tensão** (dominante-7). O gate corrige o centro `Y` do K-S para `X` **só** quando:
  1. `Y` aparece **exclusivamente como dominante-7** (nunca como acorde de repouso);
  2. esse `Y7` **resolve** uma 5ª abaixo, em `X = (Y−7) mod 12`;
  3. `X` aparece como acorde **estável** (Category.MAJOR/MINOR — um ponto de repouso).
- **Guard do blues/mixolídio:** se `Y` nunca repousa mas o alvo `X` também só aparece como
  dominante (tudo é tensão — o caso `I7-IV7-V7`), o gate **aborta** (Chediak p.121: o
  trítono do I7 de blues não resolve com expectativa → não é dominante funcional).
- **dim7 inelegível:** o gate só considera `Category.DOMINANT` (1 trítono); o coringa fica
  para change própria.
- **Ultraconservador:** dispara só quando o centro do K-S é inequivocamente um V — nunca
  toca as músicas cuja tônica descansa. Resultado validado: tônica exata 67→69%, relativa
  74→76%, centro 74→79% (Garota de Ipanema corrigida), **modo/coleção idênticos, zero
  regressão**.

**Adiado (fora desta change):** a **arbitragem modal de centro** (Arrastão→Lá) e a
**métrica de centro modal degree-relative** — ambas novas frentes de integração, vão para
uma change própria (`modal-center-arbitration`).

## Capabilities

### New Capabilities

*(nenhuma)*

### Modified Capabilities

- `key-detection`: o `detect_key` ganha o **gate de qualidade** — corrige um V detectado
  como tônica (centro do K-S aparece só como dominante-7 e resolve num alvo de repouso),
  escapando da `TIE_BAND`. A corroboração cadencial deixa de ser estritamente within-band.

## Impact

- `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py` — `_chord_infos`
  + `_tritone_gate` (gate de qualidade) e a chamada no `detect_key` após o desempate
  within-band. Reusa só `cifra_core.theory.chord_parse` (`Category`).
- `packages/harmonic_analysis/tests/test_tritone_gate.py` — unidade do gate (V-como-tônica,
  tônica em repouso, blues guard, dim7 inelegível) + não-regressão diatônica/relativa.
- `ROADMAP.md` — gate tonal feito; arbitragem modal de centro registrada como próxima.
- **TRAVA:** as 4 métricas Cifra-Club **modo/coleção idênticas** (86/97), exata/relativa
  **sobem** (67→69, 74→76) e o `center_accuracy` **sobe** (74→79). Validado ao vivo.
- **NÃO toca** `segment_keys`/modulação; não reescreve o K-S (ele faz o trabalho duro da
  coleção; o gate só corrige o centro). dim7-como-dominante e arbitragem modal: fora de escopo.
