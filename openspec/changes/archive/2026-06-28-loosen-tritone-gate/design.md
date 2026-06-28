## Context

O `_tritone_gate` ([key_detection.py:213](packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py#L213)) corrige um V detectado como tônica, mas exige que o centro K-S `Y` apareça **exclusivamente** como `Category.DOMINANT` (linha 236: `any(c is not Category.DOMINANT) → return None`). Na MPB, com sua densidade de dominantes secundários, a tônica-real-V (`Y`) é frequentemente reusada como acorde de passagem e aparece 1-2× como tríade — então o gate aborta e o erro de V-como-tônica sobrevive. São os 4 casos do "buraco de centro" (A Banda, Apesar de Você, Menino do Rio, Aquele Abraço).

A sondagem ao vivo (read-only, antes de qualquer código) revelou dois sub-padrões: três casos onde **det = V da tônica real** (a tônica real `X` é o repouso predominante, há V7 funcional → `X`) e um caso (Aquele Abraço) onde **a tônica é um `I7` de funk** e o IV parece repouso — estruturalmente diferente. Uma simulação do critério candidato contra todo o corpus deu: **corrige A Banda / Apesar / Menino do Rio, 0 regressões das corretas**, 1 troca de erro por erro neutra (Esquinas). Esta change implementa exatamente esse critério validado.

Lei do projeto ([[tritone-gate-quality-lesson]]): discriminador **funcional**, não estatístico; medir contra o baseline ao vivo; zero regressão das corretas (esta frente já barrou 2 ships).

## Goals / Non-Goals

**Goals:**
- Corrigir os 3 casos V-como-tônica onde `det = V da tônica real` (A Banda, Apesar, Menino do Rio), via um caminho ancorado no **alvo de resolução** `X`.
- Preservar o caminho restrito atual (Garota de Ipanema) e todos os guards (blues, dim7, tônica-que-descansa).
- Zero regressão das corretas; quatro métricas Cifra-Club e modo/coleção intactos.

**Non-Goals:**
- Aquele Abraço (tônica `I7` de funk) — caso distinto, fora do alcance.
- Mexer em TIE_BAND, corroboração cadencial, correção de modo paralelo, segmentação.
- Atacar o "buraco" por estatística/coleção (a abordagem que já falhou a trava 2×).

## Decisions

### D1 — Segundo caminho centrado no alvo `X`, não na pureza de `Y`

O caminho atual (A) testa se `Y` é *exclusivamente* dominante. O novo caminho (B) ignora a pureza de `Y` e testa o **alvo** `X = (Y−7) mod 12`: há V7/SubV funcional resolvendo em `X` (estrutural), `X` é repouso predominante, e `X` é âncora (1º/último acorde). *Por quê:* o sinal robusto na MPB é "a tônica de repouso ancorada que o dominante busca", não "o V nunca descansa" — secundários poluem a pureza de `Y` mas não a função de `X`. É o mesmo princípio do `verify_tonal_center` (reusado para a condição 1).

### D2 — Reusar `verify_tonal_center` para a resolução funcional

A condição 1 do caminho B (V7/SubV funcional → `X` em posição final) é exatamente `verify_tonal_center(symbols, X)` ([chediak_structural_gold.py:68](scripts/chediak_structural_gold.py#L68)). Reusar evita reimplementar o crivo do trítono e mantém um único critério de "dominante funcional resolvendo". *Alternativa rejeitada:* reescrever a detecção de cadência dentro do gate — duplicaria lógica e arriscaria divergência.

### D3 — Guards que impedem regressão

`X` deve ser **repouso predominante** (maj/min > dom na raiz `X`, ≥2) e **âncora estrutural = o PRIMEIRO acorde**. Sem o "predominante", um blues `I7→IV7` dispararia; sem a "âncora", um `V7→I` interno qualquer dispararia. A âncora é **só o primeiro acorde** (não o último): a simulação por pitch-class deu zero regressão, mas a trava ao vivo revelou que "primeiro OU último" regredia o **modo** de Esquinas (tônica Fá que FECHA na relativa Ré menor — o gate trocava major→minor). A abertura é o sinal robusto de tônica (a corroboração cadencial já pesa `CORROB_FIRST`); o último acorde engana. Com "só primeiro": corrige os 3, Esquinas não dispara, **zero regressão de tônica E de modo**.

### D4 — Caminho B só quando A não dispara; gate continua idempotente e conservador

O gate tenta A primeiro (mais estrito); se A não corrige, tenta B. Ambos retornam `(X, mode_de_X)`. A natureza ultraconservadora é preservada: nas peças corretas, `X = (det−7)` não é repouso ancorado alcançado por dominante funcional, então B não dispara (a simulação confirma: 54 não-disparos).

## Risks / Trade-offs

- **[Regressão de uma correta]** → a simulação read-only sobre o corpus inteiro deu 0; a trava ao vivo re-confirma antes de arquivar. Se aparecer 1 regressão, o ship é barrado (a regra).
- **[Esquinas: último acorde é a relativa menor]** → resolvido endurecendo a âncora para **só o primeiro acorde**: a trava ao vivo flagrou que usar o último regrediria o modo de Esquinas (Fá maior → Ré menor relativa). Com "só primeiro", Esquinas não dispara.
- **[`X` âncora por acaso]** → a conjunção tripla (funcional + predominante-repouso + primeiro-acorde) é específica; nenhum falso disparo. Caso surja no futuro, endurecer o limiar de repouso predominante.
- **[Spelling/enarmonia do alvo]** → usa classes de altura (pc), enarmonicamente robusto, como o resto de `key_detection`.

## Migration Plan

1. Adicionar o caminho B em `_tritone_gate` (após o A), reusando `_chord_infos` e `verify_tonal_center`.
2. Testes em `test_tritone_gate.py`: A Banda-like corrige via B; Garota segue via A; blues/dim7/tônica-de-repouso seguem intactos; um caso `I7`-funk não dispara B.
3. `make test` + `scripts/key_baseline.py` ao vivo: confirmar exata 69→74, centro 79→95, modo/coleção idênticos, **0 regressão**. Registrar no ROADMAP.
4. Rollback = remover o ramo B; o caminho A e o baseline anterior são o alvo de rollback.

## Open Questions

- **Aquele Abraço (`I7` funk):** vale uma change futura própria (sinal: começa/termina na tônica-dominante + SubV → tônica-dominante)? Fora do escopo aqui.
- **Âncora 1º-ou-último vs só-último:** manter a forma validada (1º ou último); endurecer só se um falso aparecer no corpus ampliado.
