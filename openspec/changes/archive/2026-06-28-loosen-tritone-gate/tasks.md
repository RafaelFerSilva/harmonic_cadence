## 1. Trava do baseline (antes de tocar código)

- [x] 1.1 Rodar `uv run python scripts/key_baseline.py` e registrar verbatim: exata, modo, relativa, coleção, centro estrutural (15/19) + a lista dos 4 buracos. Referência de zero-regressão.
- [x] 1.2 Rodar `make test` e registrar a contagem verde (referência da suíte).

## 2. Caminho B (ancorado por resolução) no gate

- [x] 2.1 Em `domain/key_detection.py::_tritone_gate`, após o caminho A (Y exclusivamente dominante) não disparar, tentar o caminho B antes de retornar None.
- [x] 2.2 Caminho B: computar `X = (ks_pc − 7) % 12`; exigir (a) `verify_tonal_center(symbols, X)` True (V7/SubV funcional → X estrutural), (b) `X` repouso predominante (maj/min > dom na raiz X, ≥2), (c) `X` é raiz do primeiro OU último acorde, (d) `X ≠ Y`. Retornar `(X, modo_de_X)` com o modo derivado da qualidade estável de X (como no caminho A).
- [x] 2.3 Reusar `_chord_infos` (categorias por acorde) e importar `verify_tonal_center` de `scripts.chediak_structural_gold` (ou replicar o crivo mínimo se o import de `scripts/` no domínio for indesejável — decidir na implementação, preferir não acoplar o domínio a `scripts/`).
- [x] 2.4 Garantir idempotência e que o caminho A e os guards (blues sem repouso aborta, dim7 inelegível, tônica-que-descansa não rebaixada) seguem intactos.

## 3. Testes

- [x] 3.1 `test_tritone_gate.py`: caso sintético tipo A Banda (Y predominante dominante mas com repouso ocasional; V7→X final; X repouso predominante e âncora) → corrige via B.
- [x] 3.2 Garota-like (Y exclusivamente dominante) → segue corrigindo via A.
- [x] 3.3 Blues `C7 F7 G7` → aborta (nenhum caminho). dim7 inelegível. Tônica-de-repouso sem dominante ancorado → não rebaixa.
- [x] 3.4 Caso `I7`-funk (tônica é dominante, impostor é o IV) → caminho B NÃO dispara (não piora).

## 4. Verificação ao vivo + docs

- [x] 4.1 `make test` verde; `make lint` limpo.
- [x] 4.2 Rodar `scripts/key_baseline.py` ao vivo; confirmar: **A Banda / Apesar / Menino do Rio corrigidos**, exata **69→74%**, centro **79→95%** (18/19), modo/coleção idênticos, **0 regressão das corretas** (Aquele Abraço pode seguir errado; Esquinas troca neutra). Se houver QUALQUER regressão de correta, barrar o ship.
- [x] 4.3 Atualizar `ROADMAP.md` (centro 79→95%, exata 69→74%; registrar os 3 corrigidos e Aquele Abraço como remanescente `I7`-funk).
- [x] 4.4 `openspec validate loosen-tritone-gate --strict` passa; pronto para `openspec archive`.
