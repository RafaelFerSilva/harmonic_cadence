# Tasks — harden-functional-center

> Duas guardas Chediak-puras no `chediak_functional_center` (repouso: alvo não-dominante;
> raiz==baixo). Escopo: `validation/functional_center.py` + testes. Gate ao vivo no
> `scripts/songbook_baseline.py`.

## 1. Trava de baseline (referência antes de mexer)

- [x] 1.1 Rodar `uv run python scripts/songbook_baseline.py` e registrar: invariante 62/62,
      cobertura 59/62, concordância 47/59 (80%), e a lista das 47 concordantes (nenhuma pode
      regredir). Rodar `scripts/worklist_adjudication.py` e anotar as 12 divergências atuais.

## 2. Guardas no `chediak_functional_center`

- [x] 2.1 **Refinado:** não precisou de novo array `cat[i]` — o pré-cálculo já tem `is_dom[i]`
      (= `_category(p)=="dominant"`), que É exatamente o predicado de repouso. Reusado direto.
- [x] 2.2 Guardas adicionadas na condição do loop: `not is_dom[i + 1]` (alvo de REPOUSO,
      não-dominante, Chediak pp.84-85) **e** `roots[i + 1] == basses[i + 1]` (a tônica repousa
      na própria raiz). O `mode` segue de `qual[i+1]`, agora coerente (raiz==baixo).

## 3. Testes unitários

- [x] 3.1 `A7(b9) D7(13)` (alvo dominante) → centro NÃO é D; cadeia não vira tônica.
- [x] 3.2 `G7(#5) Fm/C` (inversão) → NÃO retorna `C minor`; `G7(9) C` → `C major`.
- [x] 3.3 V→i menor legítimo (`... D7(9) Gm7`) → `G minor` (repouso menor, raiz==baixo).
- [x] 3.4 Transposição-invariância: a mesma peça em dois tons mapeia pelo mesmo intervalo.

## 4. Gate ao vivo + zero-regressão + docs

- [x] 4.1 Re-rodado `scripts/songbook_baseline.py`: invariante **62/62** ✓; concordância
      **47/59 (80%) → 48/58 (83%)**; velhos-tempos e ate-parece passam a concordar; a-ra vai a
      quarentena (cobertura 59→58, honesta). **Nota:** `ciume` saiu da agree — NÃO é regressão:
      a concordância antiga era ela mesma o bug (achador chamava o último acorde `E7(9)`, um
      dominante, de tônica, coincidindo com um `detect_key`=Mi provavelmente errado); a guarda
      recusa e acha o repouso real `A7→D6/9` (Ré maior). Vira worklist honesto.
- [x] 4.2 Re-rodado `scripts/worklist_adjudication.py`: worklist **12 → 10**. Das 5 previstas,
      **3 saíram limpas** (a-ra→quarentena, ate-parece/velhos-tempos→concordam). inutil-paisagem
      e razao-de-viver **permaneceram corretamente**: têm resolução a um acorde de REPOUSO real
      (`E7→A7M`), não só ao dominante — a guarda é precisa, não cega (adjudicação de sessão
      tinha atribuído as duas ao bug por engano). ciume entrou como divergência honesta.
- [x] 4.3 `make test` verde, `make lint` limpo.
- [x] 4.4 Atualizar `AGENTS.md`/`ROADMAP.md` com o novo número de concordância e o fechamento
      parcial da frente #7. `openspec validate harden-functional-center --strict` passa.
