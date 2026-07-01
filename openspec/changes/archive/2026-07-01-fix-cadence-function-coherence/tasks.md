# Tasks — fix-cadence-function-coherence

> A família autêntica/plagal só resolve na tônica quando o alvo FUNCIONA como repouso (Chediak
> XXXII p.110 — cadência = combinação D+T; XXXIII p.111 — resolução direta não é cadência).
> `analyze_cadences` consulta os `function_code`s; suprime quando o alvo é função não-repouso
> (dominante/SubV/diminuto). Escopo: `cadence.py` + call site + baseline + testes.

## 1. Trava de baseline (referência)

- [x] 1.1 Rodar o probe de coerência sobre `cifras/*.md`: registrar **5 músicas** com `V→I`-por-
      grau cujo alvo é `D2`/`Dim` (ah-se-eu-pudesse, ate-parece, avarandado, enquanto-a-tristeza,
      so-tinha-de-ser-com-voce). `songbook_baseline.py`: trítono/diminuto/D2 **62/62** (não regridem).

## 2. Guarda de função no detector de cadência

- [x] 2.1 `analyze_cadences`: novo param `function_codes: Optional[Sequence[Optional[str]]] = None`
      (alinhado por índice). Helper `_non_repose(code)`: `code.startswith("D")` ou
      `code.startswith("Sub")`.
- [x] 2.2 Nos ramos que resolvem na tônica (`b == "I"`: autêntica/imperfeita/plagal), quando
      `function_codes` está presente e o alvo `i+1` é não-repouso, **não classificar** o par
      (suprimir; não reclassificar como deceptiva — D3). Meia-cadência/deceptiva intactas.

## 3. Fiação do call site

- [x] 3.1 `services/analysis_service.py`: mover `_detailed_harmonic_analysis` para ANTES da
      chamada de cadência; extrair `[it.get("function_code") for it in harmonic_analysis]` e
      passar a `analyze_cadences`. Fonte única de função preservada.

## 4. Testes

- [x] 4.1 Guarda ativa: `["V","I"]`/`["G7","Em7"]` com `function_codes=[...,"D2"]` ⇒ par NÃO em
      Perfeita/Autêntica/Imperfeita; alvo `"Dim"` ⇒ idem; alvo `"T"` ⇒ Perfeita normal (regressão).
- [x] 4.2 Backward-compat: sem `function_codes` ⇒ comportamento grau-puro idêntico (os testes da
      taxonomia seguem verdes).

## 5. Gate ao vivo + zero-regressão + docs

- [x] 5.1 `songbook_baseline.py`: gate de coerência de cadência — alvo de cadência autêntica/plagal
      nunca função dominante/diminuta. Nasce **62/62**; provar dentes (alvo D2 falso ⇒ defeito) e
      não-vácuo (há cadências autênticas reais validadas).
- [x] 5.2 Re-rodar o probe: 5 incoerências → **0**. `songbook_baseline.py` trítono/diminuto/D2
      **62/62** (sem regressão).
- [x] 5.3 `make test` verde, `make lint` limpo.
- [x] 5.4 ROADMAP/AGENTS: marcar `fix-cadence-function-coherence` fechado (#6 fechado).
      `openspec validate fix-cadence-function-coherence --strict` passa.
