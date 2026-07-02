## Context

`classify_line` (lines.py:68-87) conta como *posição-de-acorde* apenas `is_chord_token`
(fullmatch) OU `malformed_chord_token`. Um token **acorde+decoração de resíduo vazio**
(`Am6/`, `Bb7(9)///`, `B°/A/`, `Gm7(11)///Gb7(#11)///`) é deliberadamente NÃO-malformado
(cláusula (d): resíduo vazio poupa acordes colados) e não é fullmatch — logo **não conta** na
densidade. A extração, por sua vez, resgata exatamente esses tokens via `find_all`
(lines.py:121) e a spec promete isso ("`Am7/` … the valid chord is extracted"). Resultado: em
linha com vários tokens colados, a densidade despenca, a linha vira LYRIC e é descartada
inteira, sem diagnóstico. Medido: 11 músicas, 20 linhas, ~109 acordes (dindi, samba-em-preludio
os piores).

## Goals / Non-Goals

**Goals:**
- Densidade e extração concordam sobre o que é token de posição de acorde.
- As ~20 linhas reais voltam a ser CHORD; os ~109 acordes voltam ao motor.
- Baseline re-medido (gates duros seguem verdes) e corpus re-materializado; números
  documentados atualizados.

**Non-Goals:**
- Nenhuma mudança na extração, no `malformed_chord_token`, no motor ou no threshold.
- Não tratar as outras classes da auditoria (truncamento v4/originais — change futura de
  quarentena de completude).

## Decisions

### D1 — Novo predicado `_glued_chord_token`, reusando o critério existente
Um token conta como posição-de-acorde também quando: (a) não é acorde completo nem malformado;
(b) contém ≥1 acorde válido (o regex casa); (c) o **resíduo é vazio** após remover todos os
acordes válidos e a decoração (`_RESIDUE_DECOR`) — exatamente a cláusula (d) do
`malformed_chord_token` invertida. Não é heurística nova: é o mesmo teste, com o veredito
oposto, e espelha o que `find_all` extrai. Palavra de letra não entra: `Dado/` → remove `D`,
resíduo `ado` ≠ vazio.

### D2 — Predicado na densidade, não no `_DECOR`
*Alternativa considerada:* pré-processar o token (strip de `/`+ finais) antes do fullmatch —
rejeitada: mudaria a semântica de `is_chord_token` (API pública usada em outros pontos) e não
cobriria o colado composto (`X///Y///`). O predicado novo é local à densidade.

### D3 — Generalizar decoração pura no denominador
`_DECOR` é um frozenset literal (`"/", "|", "//", …`) que não contém `"///"` — um token só-
decoração de 3+ barras hoje conta no denominador e dilui a densidade. Generalizar para
"token composto só de caracteres de decoração" (regex `^[/|%\-—·]+$`), coerente com o texto da
spec ("tokens de decoração não contam no denominador"). Mesma família do bug, uma linha.

### D4 — Re-medição é parte da change, com política de pausa
Após o fix: `songbook_baseline.py` (os 3 gates duros DEVEM permanecer 170/170 — um acorde
recuperado que viole gate é **pausa-e-investiga**, nunca ajuste do gate) e `corpus build` +
`report` (corroboração de centro e ledger de trítono podem legitimamente mudar — atualizar
AGENTS.md com os números novos, citando esta change).

## Risks / Trade-offs

- **[Falso-positivo de densidade em letra]** → o resíduo-vazio é restritivo: exige que TODO o
  token seja acordes+decoração. Palavras com prefixo-acorde deixam resíduo (`Brasil`→`rasil`).
  Risco residual: token de letra de uma letra + barra (`E/`) — raro, e a extração de raiz nua
  segue gated pela whitelist.
- **[Números documentados mudam]** → esperado e desejado (o dado estava errado); a change
  atualiza AGENTS.md/ROADMAP na mesma passada.
- **[Gate quebrar com dado novo]** → política explícita (D4): investigar antes de qualquer
  mudança em gate; o invariante é de Chediak, não do corpus.

## Migration Plan

Aditivo/local (2 funções em lines.py). Rollback = reverter o commit. O corpus persistido é
regenerável (`corpus build` re-materializa com o motor corrigido; `analysis_run` novo preserva
o snapshot antigo para comparação A/B — é o caso de uso do D3 da persistência).

## Open Questions

- Nenhuma bloqueante.
