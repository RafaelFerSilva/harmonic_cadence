## Context

O harness (`validation/key_accuracy.py`) compara o tom detectado com o anotado (gold =
tom do Cifra Club) em 4 métricas: modo, tônica-exata, relativa-consciente, coleção. Todas
contra **um** ouro (Cifra Club), honesto para a tônica-exata ABSOLUTA. Falta uma métrica
que isole o erro de **centro estrutural** (mediante; tonal↔modal), e um ouro confiável
para ele — o Chediak.

## Goals / Non-Goals

**Goals:**
- Um 2º ouro (Chediak) e uma métrica `center_accuracy` invariante a transposição.
- Quantificar o "buraco" de centro que a change 2 (gate do trítono) vai atacar.
- Zero mudança de detecção; as 4 métricas Cifra-Club ficam idênticas.

**Non-Goals:**
- Alterar `detect_key`/`segment_keys`/`TIE_BAND`/`cadence_corroboration` (change 2).
- Ingerir a Parte 4 do Chediak (só fatos citados).
- Substituir a tônica-exata; `center_accuracy` é aditiva.

## Decisions

### D1 — Centro medido por OFFSET, invariante a transposição

A métrica não compara a altura absoluta — compara a **relação de grau** entre o centro
detectado e o tom do Cifra Club (a âncora do arranjo raspado):

```
acerto_de_centro(música) ⟺ (detected_tonic_pc − cc_key_pc) % 12 == structural_offset
```

`cc_key_pc` (tom do Cifra Club) e `detected_tonic_pc` (do `detect_key` sobre os MESMOS
acordes raspados) vivem no mesmo espaço de altura → o offset é preservado sob qualquer
transposição do arranjo. Foco na **tônica/centro** (pitch), não no rótulo maior/menor —
o modo já tem `mode_accuracy`.

### D2 — Descontaminação: `cc_key` é ÂNCORA, nunca FONTE da verdade do centro

O `cc_key` tem dois papéis que NÃO podem se confundir: (1) âncora de transposição (em que
tom os acordes raspados estão — uso limpo) e (2) fonte da verdade do centro (qual grau é a
tônica — **contaminado** por anotação crowdsource ingênua: relativa, transposição por
tessitura, miopia modal). Tratar `offset = 0` como **default** funde os dois e carimba o
erro do Cifra Club como gold. Então invertemos o ônus da prova: **nada é gold até ser
verificado de forma independente.** Cada música carrega uma **proveniência**:

```
  TIER A — chediak       centro do livro, página citada (Arrastão p125, …)
                         → autoridade incontestável; RESERVADO p/ validação
                           NÃO-CIRCULAR da change 2 (o gate tem que recuperá-lo
                           sem ter sido calibrado nele)
  TIER B — verified      centro confirmado por critério mecânico DOCUMENTADO:
                         a peça tem V7 funcional (trítono real) resolvendo no cc_key
                         em cadência estrutural/final → cc_key é tônica por Chediak
                         (p.84), não por "achismo da internet"
  TIER C — unverified    nem A nem B → QUARENTENA: NÃO entra no center_accuracy;
                         contado à parte (cobertura visível)
```

`center_accuracy` é reportado **só sobre A+B**; o Tier C fica isolado. Assim o número nunca
é poluído por anotação não-crivada. O `structural_offset` segue a regra do D1 (0 quando o
centro verificado = cc_key; ex.: Arrastão offset 7, Tier A, p.125), mas o offset 0 agora é
uma **afirmação verificada**, não um palpite herdado.

Anti-circularidade: o Tier B usa "tem V7→cc_key", que se parece com o gate da change 2 —
por isso o **Tier A (Chediak puro, sem critério de dominante) é a âncora de validação**; e
mesmo no Tier B a change 2 faz mais que o crivo (gera o candidato, passa os 4 filtros incl.
coleção, escapa a banda). Disciplina de anotação **cega**: decidir o centro por
Chediak/teoria PRIMEIRO, só então comparar ao cc_key — nunca ler o cc_key e racionalizar.

### D3 — Muro de copyright: só fatos, sem Parte 4 ingerida

Cada entrada é um fato `(música, cc_key, structural_offset, center_type, modo,
provenance, justificativa)` — onde `provenance ∈ {chediak, verified, unverified}` e
`justificativa` é a página citada (Tier A) ou o critério mecânico observado (Tier B, ex.:
"G7→C final, compasso N"). Páginas da Parte 2 (pp.121-127, já extraídas) e, pontualmente,
tons citados da Parte 4 (só o fato música→tom→modo). NUNCA as harmonizações/cifras/
tabelas. Acordes do Cifra Club.

### D4 — Aditiva; baseline Cifra-Club intacto

`center_accuracy` entra como chave nova em `evaluate_corpus` e como 5ª linha no baseline.
As 4 métricas Cifra-Club e o verdict atual ficam idênticos. O baseline ganha um **verdict
de divergência** por música quando `structural_offset ≠ 0` (Cifra Club e Chediak
discordam), tornando a divergência visível em vez de escondida.

### D5 — O "buraco" é o entregável da medição

Rodar a métrica HOJE (antes do gate) quantifica quantas das n=60 erram o centro
estrutural — mediantes (Lilás, Açaí…) + modais (Arrastão…). Esse número é o **alvo** que a
change 2 vai mover. A change 1 não melhora nada; ela torna o ganho da change 2 mensurável.

### D7 — A validação restringiu o escopo a TONAL (achado, não plano)

Rodar a métrica ao vivo pescou uma contaminação no offset modal: derivá-lo por subtração
absoluta `(centro_Chediak − cc_key)` só vale quando Chediak e o Cifra Club estão na MESMA
transposição. Falso em *Pra Não Dizer* (Chediak Mi eólio, CC Fá menor → off=11 punindo uma
detecção CORRETA) e suspeito em *Procissão* (coleções diferentes). Decisão: **a change 1
mede só o centro TONAL** (offset 0, verificado por dominante funcional); os fatos modais do
Tier A ficam committados como âncora, mas o **centro modal** (offset ≠ 0) vai para a change
de arbitragem modal, que deriva o offset pelo grau do final na coleção, não por altura
absoluta. O buraco tonal revelado: **74% (14/19 verificados)** — 5 casos de
**V-detectado-como-tônica** (Garota F→C, A Banda D→A, Aquele Abraço E→A, Apesar D→A, Menino
do Rio F→C), todos offset 0, alvo limpo do gate do trítono. As 4 métricas Cifra-Club:
idênticas (86/67/74/97).

## Risks / Trade-offs

- **Risco: o offset modal embute uma teoria (o final é o V do parente maior).** Mitigação:
  cada override cita a página do Chediak e o offset é derivado do fato (cc_key, centro
  Chediak), não chutado. Documentado caso a caso no fixture.
- **Trade-off: `center_accuracy` ≈ tônica-exata onde não há divergência.** É esperado: o
  valor novo está nos casos modais e em reenquadrar o gold como estrutural (Chediak), que
  é o que a change 2 precisa medir contra. Não é redundância — é o eixo de medição do 3b.
- **Risco: poucos casos modais no n=60 (amostra pequena).** Mitigação: somar os exemplos
  modais da Parte 2 (Ponteio, Canto de Ossanha, etc.) ao corpus de centro; expansão via
  tons citados da Parte 4 fica disponível, caso a caso.
