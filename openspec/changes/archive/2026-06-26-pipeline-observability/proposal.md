## Why

Toda seção opcional da análise (modal, cifra romana, condução de vozes,
escala-acorde, parsing funcional, reharmonização, explicação, regiões tonais)
está num `try/except` que **engole a exceção** e devolve `[]`/`None`/`{}`. Há
ainda um `print("Aviso: ...")` no lugar de `logging`.

Resultado: um `[]` significa *"nada se aplica"* **ou** *"estourou"* — e não dá
pra distinguir. Depois da Sina (a análise *pode* errar em silêncio), isso pesa:
o sistema é uma caixa-preta. E é pré-requisito da Fase A — um corpus run que
"sucede" mas teve 3 seções caindo em silêncio poluiria as métricas.

## What Changes

- **Helper `_safe_section`**: executa a seção; em falha, devolve o default,
  **loga** (warning) E **registra** em `result["diagnostics"]` `{section, error}`.
- **`result["diagnostics"]`**: lista (vazia = tudo ok; preenchida = seções
  degradadas) — torna "vazio porque nada se aplica" distinguível de "vazio
  porque estourou".
- Trocar o `print("Aviso:")` por `logging`.
- O relatório **JSON** expõe `diagnostics` (é dado estrutural).

Fora de escopo: UI de diagnóstico nos relatórios humanos (Markdown/HTML) —
follow-up; instrumentação de latência/métricas.

## Capabilities

### New Capabilities
- `analysis-diagnostics`: seções opcionais degradam de forma **observável**
  (logadas + registradas), nunca em silêncio.

## Impact

- `harmonic_analysis/services/analysis_service.py`: logger de módulo;
  `_safe_section`; as 8 seções passam por ele; `diagnostics` no resultado.
- `presentation/reports/json.py`: expõe `diagnostics`.
- Testes: run limpo → diagnostics vazio; seção que estoura → registrada + default.
