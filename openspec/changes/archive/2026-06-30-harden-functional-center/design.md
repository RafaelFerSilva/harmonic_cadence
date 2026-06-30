## Context

`chediak_functional_center` (`validation/functional_center.py`) acha a tônica ancorando o
candidato nos repousos estruturais (último, depois primeiro acorde) e confirmando por um
dominante real (trítono) que resolve nele pelo baixo. O loop atual aceita QUALQUER acorde-alvo:

```python
if is_dom[i] and roots[i] in (dom, subv) and basses[i + 1] == cand:
    mode = "minor" if qual[i + 1] == "minor" else "major"
    return cand, mode
```

Dois furos, ambos contra *"tônica repousa, V é tensão"* (Chediak pp.84-85), provados na worklist:
- O alvo `basses[i+1]` pode ser ele próprio um **dominante** (`D7`, `B7`): o achador chama de
  tônica um elo de cadeia V/V→V. (a-ra, ate-parece, inutil-paisagem, razao-de-viver)
- O alvo pode ser uma **inversão** (`Fm/C`): `basses[i+1]` é o baixo `C`, mas `qual[i+1]` é a
  qualidade do `Fm` — cunha "Dó menor" de um Fá menor. (velhos-tempos)

Hoje o código guarda só `roots`, `basses`, `is_dom`, `qual` por acorde — não guarda a categoria
do alvo nem se raiz==baixo.

## Goals / Non-Goals

**Goals:**
- O alvo da resolução só estabelece tônica se for **repouso**: não-dominante **e** raiz==baixo.
- Zero regressão das 47/59 que hoje concordam; corrigir velhos-tempos; quarentenar a-ra.
- Permanecer transposição-invariante e annotation-free (nada de `cc_key`).

**Non-Goals:**
- `detect_key`, motor de análise, invariante funcional, trava de trítono do 3b — intocados.
- Não tentar "seguir a cadeia" até o fim (achar a tônica real de a-ra): quarentena honesta
  basta; `detect_key` continua oferecendo seu palpite. Seguir a cadeia é trabalho futuro.

## Decisions

**D1 — Predicado de repouso = `Category` ≠ `DOMINANT` no acorde-alvo.**
Para saber a categoria do alvo, parsear o símbolo do alvo e checar `category()`. Já existe
`_category(p)` no módulo; estender o pré-cálculo para guardar `cat[i]` (categoria por índice) e
testar `cat[i+1] != "dominant"`. Coerente com o invariante funcional do baseline (que usa a
mesma `Category.DOMINANT`). *Alternativa rejeitada:* checar só "tem sétima menor" — `Category`
já encapsula o trítono real (3M+7m), é a fonte única.

**D2 — Predicado raiz==baixo no acorde-alvo.**
Guardar `roots[i]` (já existe) e `basses[i]` (já existe) e exigir `roots[i+1] == basses[i+1]`
no alvo. Com isso, o `mode` derivado de `qual[i+1]` passa a ser sempre da raiz certa (some o
caso `Fm/C`). *Alternativa rejeitada:* usar a raiz do alvo como centro (em vez do baixo) — muda
a semântica de "ancorar no baixo do repouso" e arrisca casar acordes não-estruturais; raiz==baixo
é a guarda mínima e fiel ao texto ("a tônica repousa na própria raiz").

**D3 — Guardas aplicadas DENTRO do loop de confirmação, candidatos inalterados.**
Os candidatos a tônica continuam sendo os extremos (`valid_bass[-1]`, depois `[0]`). As guardas
filtram a *confirmação* (o alvo da resolução), não a *escolha* do candidato. Assim, quando o
extremo é um dominante/inversão e não há resolução a repouso, retorna `None` (quarentena) — o
comportamento honesto desejado.

## Risks / Trade-offs

- **[Cobertura cai (mais quarentena)]** → Mitigação: é o resultado CORRETO — quarentena honesta
  substitui centro errado; o baseline reporta cobertura separada, então nada é mascarado. O gate
  exige que nenhuma das 47/59 concordantes regrida.
- **[Uma peça legítima que termina num acorde com 7m de tônica-blues (`I7`)]** → o alvo seria
  `Category.DOMINANT` e seria rejeitado. Mitigação: esse caso já é tratado no caminho do MOTOR
  pelo gate `i7-funk-anchor` (Aquele Abraço), que é OUTRO caminho; aqui no achador de
  CORROBORAÇÃO, perder esse centro vira quarentena (honesto), não erro. Medir no baseline.
- **[Parse do símbolo do alvo pode falhar]** → já há `try/except` no pré-cálculo (preenche
  `is_dom=False`, etc.); estender para `cat`/raiz==baixo com o mesmo fallback seguro.

## Migration Plan

1. Estender o pré-cálculo do `chediak_functional_center` para guardar a categoria por índice
   (`cat[i]`) — já há `roots`/`basses`.
2. Adicionar as duas guardas na condição do loop: `cat[i+1] != "dominant"` e
   `roots[i+1] == basses[i+1]`.
3. Testes unitários: `A7(b9)→D7(13)` (dominante-alvo) → None; `G7(#5)→Fm/C` (inversão) não vira
   "C minor"; `G7(9)→C` (repouso, raiz==baixo) → `C major`; um V→i menor legítimo
   (`D7→Gm7`) → `G minor`; transposição-invariância.
4. **Gate ao vivo:** `scripts/songbook_baseline.py` antes/depois — invariante 62/62; concordância
   ≥ 47/59; zero regressão das concordantes; velhos-tempos corrige, a-ra quarentena.
   `scripts/worklist_adjudication.py` — as 5 saem. `make test`/`make lint`.
5. Rollback trivial: reverter o commit; nenhuma migração de dado.

## Open Questions

- Nenhuma bloqueante. (Seguir a cadeia de dominantes até a tônica real — p.ex. resolver a-ra
  para o centro verdadeiro em vez de quarentena — fica para uma frente futura, fora do escopo.)
