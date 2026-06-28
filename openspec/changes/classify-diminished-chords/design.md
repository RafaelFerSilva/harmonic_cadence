## Context

`HarmonicAnalysis.analyze_function` ([harmony.py:89](packages/harmonic_analysis/src/harmonic_analysis/domain/harmony.py#L89)) classifica o diminuto assim hoje: o ramo `0c` (`dim7-as-dominant`) pega o **ascendente** (resolve ½t acima → `Dsec`/`D`); todo o resto cai na seção `5b` "Empréstimo Modal" (`degree is None → Emp`), porque os diminutos não-dominantes são cromáticos. A sondagem ao vivo confirmou: `Ab°7→G` (descendente) e `C#°7` entre dois `C` (auxiliar) retornam `Emp` — teoricamente errado.

Dois fatos da sondagem guiam o design: (1) o ramo `"Dim"` na seção 1 (linhas 205–218) virou **código morto** — exige `interval_next == 1`, exatamente o que o `0c` intercepta antes; (2) **nenhum** diminuto é legitimamente `Emp` (empréstimo modal é tríade/tétrade maior/menor de modo paralelo). Logo, mover TODO diminuto não-dominante para uma classificação própria é correção pura, sem risco semântico.

A change é puramente na **camada de função/rotulagem** — não toca `detect_key`, então o baseline fica idêntico. A trava é a suíte de testes.

## Goals / Non-Goals

**Goals:**
- Classificar o diminuto não-dominante por tipo (auxiliar / descendente / passagem) conforme Chediak XXI–XXII, tirando-o de `Emp`.
- Preservar o ascendente→dominante e o `vii°7`.
- Limpar o ramo `"Dim"` morto.

**Non-Goals:**
- Numeral romano de diminutos cromáticos descendentes/auxiliares (`roman.py`) — fica como está; a change é sobre função, não notação.
- Mexer em `detect_key`, escala-acorde (a octatônica já cobre todo diminuto), ou cadências.
- Subtipos mais finos do Chediak (ascendente-de-passagem vs auxiliar-superior/inferior) — o rótulo genérico "Diminuto" cobre o resíduo.

## Decisions

### D1 — Novo ramo `0d` para o diminuto não-dominante, antes de `Emp`

Inserir, logo após o bloco `0c` (que retorna para o ascendente-dominante), um ramo `if chord.quality == "diminished":` que classifica por tipo e retorna o código `"Dim"` com nome/descrição do subtipo. Por vir antes da seção 5b, intercepta os cromáticos que hoje viram `Emp`. *Por quê o code `"Dim"`:* já existe no enum `FunctionCode` e na constante `HARMONIC_FUNCTIONS["Dim"]`; reusar evita um código novo e mantém a saída estável (o subtipo vai no nome/descrição).

### D2 — Classificação pela motion da fundamental (a harmonia, que é o que temos)

- **Auxiliar:** `_get_interval(prev.root, next.root) == 0` (prev e next são o mesmo acorde — bordadura).
- **Descendente:** `_get_interval(next.root, chord.root) == 1` (o `next` está ½t abaixo da fundamental do diminuto).
- **Genérico ("Diminuto"):** o resto (sem `prev`/`next`, ou motion que não casa). *Por quê fiel:* Chediak XXI classifica justamente pela direção da fundamental (ascendente/descendente) e pelo retorno (auxiliar); o ascendente já saiu pelo `0c`.

### D3 — Remover o bloco `"Dim"` morto da seção 1

Apagar o `if func_code == "Dim": ...` (linhas 205–218): ofuscado pelo `0c` (diminutos diatônicos `vii°/#iv°` viram dominante). Com o `0d` cobrindo todo diminuto, a seção 1 nunca mais vê um diminuto. *Alternativa rejeitada:* deixar o bloco morto — polui e confunde.

## Risks / Trade-offs

- **[Regressão de um rótulo correto]** → nenhum diminuto era legitimamente `Emp`; nenhum teste prende diminuto em `Emp` (verificado). A suíte completa roda como trava.
- **[Ordem de precedência auxiliar vs descendente]** → auxiliar (`prev == next`) é checado primeiro; um caso que seja ambos (raro) é lido como auxiliar, o que é o correto (a bordadura tem prioridade semântica).
- **[Diminuto sem contexto (1º/último acorde, sem prev/next)]** → cai no genérico "Diminuto"; aceitável (sem vizinhos não há direção a classificar).
- **[Baseline]** → impossível regredir: `detect_key` não é tocado.

## Migration Plan

1. Adicionar o ramo `0d` em `analyze_function`; remover o bloco `"Dim"` morto.
2. Testes: descendente (`Ab°7→G`), auxiliar (`C C#°7 C`, `Dm D#°7 Dm`), ascendente segue dominante, `vii°7` intacto, e o invariante "nenhum diminuto vira `Emp`".
3. `make test` + `make lint`; rodar `scripts/key_baseline.py` ao vivo para confirmar baseline **idêntico** (sanidade — não deve mudar).
4. Atualizar `ROADMAP.md`. Rollback = remover o ramo `0d` e restaurar o bloco `"Dim"`.

## Open Questions

- O rótulo genérico "Diminuto" merece ser refinado em "ascendente de passagem" vs "descendente de passagem" numa v2? Por ora o resíduo é pequeno; manter simples.
