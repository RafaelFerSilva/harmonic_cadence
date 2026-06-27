## Context

`detect_key` (`domain/key_detection.py`) é K-S puro: `pitch_class_profile` acumula as
classes de altura realizadas (com peso na fundamental e no acorde final), e
`detect_key` correlaciona (Pearson) contra os 24 perfis Krumhansl-Kessler, ordena e
devolve o melhor `KeyEstimate` (com `alternatives`). O histograma é invariante a
ordem e função — perde justamente os marcadores de centro tonal.

A exploração (varredura + simulação no corpus n=28, gold = tom Cifra Club) estabeleceu:
- A confusão **relativa** é um quase-empate estrutural: maior e relativa menor
  compartilham a coleção diatônica → perfis K-S quase idênticos → o tom certo é
  tipicamente o #1/#2 alternativo do próprio K-S. Um desempate funcional resolve.
- O desempate vem de **teoria funcional do Chediak**: as 5 cadências (XXXII, pp.
  109-111) e o acorde final como tônica. V→I (maior) vs V→i (menor) e o baixo final
  fixam o centro tonal onde o histograma é cego.
- Simulação: desempate conservador (re-rank só na banda EPS) → modo 64%→71%, exata
  46%→54%; **nenhuma música correta quebrada**.

## Goals / Non-Goals

**Goals:**

- Reduzir a confusão maior↔relativa-menor adicionando corroboração cadencial sobre o
  K-S, **sem** alterar a forma de `KeyEstimate` nem a arbitragem/segmentação a jusante.
- Agir **apenas** no quase-empate (banda EPS) — nunca sobrepor um K-S confiante.
- Fundamentar cada sinal em teoria funcional (Chediak), não heurística ad-hoc.

**Non-Goals:**

- Override agressivo (resolveria a paralela-erro tipo *Valsinha*, K-S confiante e
  errado) — risco de regressão; follow-up medido.
- Segmentar modulações reais (*Wave*/*Chega de Saudade*) — é `segment_keys`, não
  estimativa pontual.
- Tônica de modos de igreja pelo K-S.
- Maximizar métrica in-sample tunando EPS — anti-objetivo explícito.

## Decisions

**1. Estágio de corroboração sobre o ranking, não dentro do perfil.**
O sinal é categórico-funcional (cadência, acorde final), não estatístico; somá-lo ao
histograma o diluiria. Decisão: computar o ranking K-S como hoje, depois re-rankear na
banda de empate. Alternativa (mais peso cadencial no `pitch_class_profile`): rejeitada
— já há `CAD_W=2` e não resolve; aumentar regride quem não termina na tônica.

**2. Banda de quase-empate (EPS), conservadora.**
Re-rankear só candidatos com `score >= top - EPS`. Garante que o estágio só decide
quando o K-S está **genuinamente ambíguo** — o caso da relativa, que é um empate por
construção. Fora da banda, K-S manda. Isto é o que tornou a simulação livre de
regressão sobre acertos.

**3. Pontuação de corroboração (sinais do Chediak):**
Para um candidato `(tônica t, modo m)`, sobre a sequência de acordes:
- 1º acorde assenta em `t`: **+1** (abertura no centro).
- Último acorde assenta em `t`: **+2**; e, **se for a tônica de fato** (raiz `== t`),
  **+1** se a qualidade casa `m`, **−1** se o modo está trocado.
- **Cadência autêntica** nos últimos ~4 acordes: um acorde de função dominante
  resolvendo na tônica → **+3** (marcador mais forte). `G7→C` pontua Dó maior;
  `E7→Am` pontua Lá menor.

Dois refinamentos que a implementação forçou (e que melhoram a teoria, não só o
corpus):
- **Âncora = baixo, não a fundamental** (lição da Sina, redescoberta como regressão:
  o teste da Sina quebrou porque `D/A` creditava "termina em Ré"). "Assenta na
  tônica" e o alvo da cadência usam o **baixo** (`p.bass or p.root`); a fundamental
  só identifica o acorde dominante (a identidade do V independe da inversão).
- **Cadência = V OU SubV** (substituto tritonal `bII7→I`): ambos função dominante
  resolvendo na tônica, idiomáticos em bossa/MPB. Identidade `root == (t+7)` **ou**
  `root == (t+1)`.

Pesos num único bloco nomeado (`CORROB_*`, `TIE_BAND`), recalibráveis contra o
corpus, **não** maximizados in-sample.

**Resultado in-sample (n=28, EPS=0.06):** modo 64%→68%, exata 46%→50%, relativa 61%
(estável). *Sampa* virou (`A menor`→`C maior`, de "relativo" para "exato"); a Sina e
o gate sintético seguem intactos (255 testes). *Papel Marché* não virou — ficou
**fora da banda** (gap ~0.07), não por tipo de cadência; alargar o EPS para pegá-lo
seria in-sample chasing, evitado de propósito. Ganho modesto e honesto; a validação
real é a ampliação do corpus.

**4. EPS escolhido conservador, não in-sample-ótimo.**
A simulação mostrou ganho crescente com EPS (até 0.12), mas EPS largo deixa de ser
"empate" e vira "cadência manda" (overfit). Decisão: fixar um EPS modesto (ordem de
~0.05–0.08, a confirmar), documentado como parâmetro a validar com corpus maior, e
**não** travá-lo no valor que maximiza as 28 músicas.

**5. Resultado e contrato preservados.**
`detect_key` devolve o mesmo `KeyEstimate`; `alternatives` segue do ranking K-S. Os
consumidores (`_mode_refines_key`, `segment_keys`, relatórios) não mudam.

## Risks / Trade-offs

- **[Overfit do EPS/pesos no n=28]** → Mitigação: EPS conservador e principiado;
  pesos num só ponto; ganho reportado como *indicativo*; corpus ampliado é a validação
  contínua. Caracterizar casos-alvo nominais (Sampa, Papel Marché, As Rosas) em teste.
- **[Regressão silenciosa em música que termina fora da tônica]** (fade-out, final em
  IV/vi) → Mitigação: a banda EPS limita a ação ao quase-empate; cadência só pontua se
  o padrão dominante→tônica existe de fato; gate sintético `test_key_corpus` (100%)
  trava regressão diatônica clara.
- **[Sinais conflitantes]** (1º acorde aponta um, cadência outro) → a cadência tem o
  maior peso (+3) por ser o marcador mais forte de centro tonal; é uma escolha
  teórica, registrada.
- **Trade-off:** não resolve a paralela-erro nem modulação real — aceito, são
  follow-ups com mecanismo próprio (override medido / segmentação).

## Migration Plan

1. Testes de caracterização: alvos que devem virar (Sampa→C maior, Papel Marché→C
   maior, As Rosas→Dm) e invariantes (o `test_key_corpus` sintético continua 100%).
2. Implementar `cadence_corroboration(symbols, tonic, mode)` e o re-rank na banda EPS
   dentro de `detect_key`, sem mudar a assinatura.
3. Rodar o baseline (rede) e registrar o ganho in-sample; rodar a suíte offline.
4. Se algum alvo não virar ou um acerto regredir, ajustar pesos/EPS de forma
   principiada (não para casar o n=28), ou documentar como limite do v1.

## Open Questions

- Valor exato de EPS: fixar agora (~0.05–0.08) e revisitar com corpus maior, ou
  parametrizar e medir uma pequena varredura honesta? (preferência: fixar conservador,
  documentar).
- A cadência deve considerar inversões/baixo cifrado (`G7/B → C`) como autêntica? (o
  baixo é função; candidato a refinamento, mas o v1 pode usar a fundamental).
