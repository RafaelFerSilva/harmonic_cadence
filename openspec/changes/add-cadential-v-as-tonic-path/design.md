## Context

`_tritone_gate` corrige o V-como-tônica por dois caminhos: A (`_exclusive_dominant_path`, Y só
dominante) e B (`_anchored_resolution_path`, Y descansa às vezes, cadência na **janela final** +
X=1º acorde). A worklist n=170 mostrou casos que abrem com o `V→I` (a cadência não está no fim):
`a-volta` (K-S=G, tônica C, `G7→C7M` na abertura), `dia-de-vitoria` (K-S=E, tônica A). O Path B os
perde porque `_functional_dominant_resolves` só varre `CADENCE_WINDOW` acordes finais.

Probe (n=170, varredura peça-inteira ingênua, só X=1º acorde): 8 mudanças — 3 boas
(`a-volta`→C, `dia`→A, `atras`→F#) e 5 ruins (`domingo-azul`/`esse-mundo-e-meu` fecham na tônica
real; `eh-menina`/`tempo-feliz` abrem no IV/iv com 1 tonicização; `o-amor` modulante). Duas
guardas separam os bons dos ruins.

## Goals / Non-Goals

**Goals:** corrigir o V-como-tônica cadenciado na abertura, sem regredir os detect-certo nem as
concordâncias; aditivo (Paths A/B intactos); transposição-invariante; Chediak-puro.

**Non-Goals:** K-S pegando o IV/ii/iii/relativa (outras geometrias); a armadilha do ii-V (achador
funcional preferir o alvo do V ao ii — frente separada); mexer nos Paths A/B.

## Decisions

**D1 — Path C é ADITIVO (novo `_cadential_resolution_path`), não altera A/B.** `_tritone_gate`
tenta A → B → C, primeiro que casar vence. Preserva A Banda/Apesar/Menino do Rio (Path B) verbatim
— crítico porque essas músicas CC não estão em `cifras/` e não são testáveis no baseline atual.
*Alternativa rejeitada:* relaxar o Path B (varrer peça inteira) — arrisca quebrar A Banda et al.
(untestável) e é net-negativo sem as guardas novas.

**D2 — Guarda cadencial `≥2 resoluções V→X` (peça inteira).** O tônico é confirmado por resolução
**repetida**; um IV/iv que recebe UMA tonicização passageira (`eh-menina` abre `G7M`, tônica D;
`tempo-feliz` abre `Am7`, tônica Em — 1 resolução cada) não passa. É o discriminador que a
janela-final dava de graça (a cadência final é estrutural); fora da janela, exige-se repetição.
*Alternativa rejeitada:* `≥1` — deixa passar `eh-menina`/`tempo-feliz`.

**D3 — Guarda estrutural `NÃO termina em Y-repouso`.** Espelho da âncora de abertura (X=1º): se o
K-S `Y` **descansa (maj/min) no último acorde**, `Y` é a tônica confirmada no fecho estrutural
(Chediak: repouso final) → aborta. Pega `domingo-azul` (abre `G7M` no IV, mas FECHA em `D`=tônica)
e `esse-mundo-e-meu` (abre `F7M` no IV, fecha em `C`=tônica) — abrir no IV + `V→IV` (blues I7→IV ou
tonicização) é localmente idêntico a V-como-tônica; o fecho na tônica real desempata.

**D4 — Reusa as guardas do Path B: X repouso predominante (rest>dom, rest≥2) + X=1º acorde + X≠Y.**
Mantém a conservação (só a abertura estabelece a tônica; o último acorde engana — Esquinas).

**D5 — Modo por `_x_mode(present, X)`** (qualidade estável dos acordes em X), como os Paths A/B.

## Risks / Trade-offs

- **[`atras-da-porta` fica F# maior, func diz F# menor]** → tônica corrigida (progresso), mas a
  divergência de MODO permanece; não é regressão (era divergente, segue divergente). O
  `_correct_parallel_mode` decide o modo a jusante.
- **[`o-amor-e-chama` modulante muda B→E]** → peça sem tônica global; nem cria nem perde
  concordância (func=Eb). Aceitável (E é a abertura `Em7 Bm7`).
- **[Overfit às 8 músicas?]** → as guardas são estruturais/cadenciais (Chediak), não arbitrárias;
  validadas por simulação em TODO o corpus (só 4 mudam, +2 concordâncias, 0 regressão, gates
  170/170). O critério nasce conservador.

## Migration Plan

1. `_cadential_resolution_path(infos, present, ks_pc)` em `key_detection.py` (guardas D2-D5).
2. `_tritone_gate`: após A e B, tenta C.
3. Testes: `a-volta`-like (`C7M Am7 Dm7 G7 C7M ...`) → corrige p/ C; `eh-menina`-like (1 resolução)
   → NÃO corrige; fecha-na-tônica (`... D7M`) → NÃO corrige; sintético do Path B intacto.
4. **Gate ao vivo:** baseline n=170 — concordância 121→**123**, 4 gates **170/170**, sem regressão;
   `make test`/`make lint`.

## Open Questions

- Nenhuma bloqueante. A armadilha do ii-V (achador preferir o alvo do V ao ii) e as geometrias
  IV/ii/iii/relativa ficam para frentes futuras (documentadas na worklist).
