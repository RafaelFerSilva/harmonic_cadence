# Design — Observabilidade do pipeline

## O problema: degradação silenciosa

```python
try:
    result["voice_leading"] = voice_leading.analyze(all_chords)
except Exception:
    result["voice_leading"] = {}          # estourou? nada se aplica? indistinguível
```

Repetido em 8 seções, mais um `print("Aviso:")`. A robustez (uma seção quebrada
não derruba o relatório) é boa — o problema é a **invisibilidade**.

## A solução: degradar visível

Um helper centraliza o padrão e adiciona observabilidade:

```python
def _safe_section(self, result, name, compute, default):
    try:
        result[name] = compute()
    except Exception as e:
        result[name] = default
        logger.warning("seção '%s' degradou: %s", name, e)
        result["diagnostics"].append({"section": name, "error": f"{type(e).__name__}: {e}"})
```

- **`logging`** (não `print`): a aplicação/CLI decide os handlers; em produção vai
  pra onde tiver que ir.
- **`result["diagnostics"]`** (inicializado `[]`): vazio ⇒ tudo ok; preenchido ⇒
  estas seções caíram. É o sinal que faltava — e o que blinda a Fase A (o corpus
  run vê as degradações em vez de mascará-las).

## Onde aparece

- No **resultado** (`analyze_song_data_structured`) — consumidores diretos
  (testes, CLI, Fase A) veem.
- No relatório **JSON** (export de dados — lar natural de diagnóstico estrutural).
- Relatórios humanos (Markdown/HTML): follow-up.

## Não-objetivos

- Métricas de latência / instrumentação de performance.
- UI de diagnóstico nos relatórios humanos.
- Mexer no caminho fatal (normalização/extração já retornam `{"success": False}`).
