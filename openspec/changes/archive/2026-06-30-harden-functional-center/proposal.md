## Why

A adjudicação da worklist limpa (n=12, pós-`sanitize-chord-extraction`) mostrou que **5 das 12
divergências `detect_key` × `chediak_functional_center` são erros do PRÓPRIO achador funcional**,
não do `detect_key` — e ambos violam o princípio do projeto *"tônica repousa, V é tensão"*
(Chediak pp.84-85):

1. **Dominante-como-tônica** (a-ra, ate-parece, inutil-paisagem, razao-de-viver): o achador
   aceita como tônica um acorde-alvo que tem **trítono real** (`D7`, `B7`, `A7` —
   `Category.DOMINANT`) só porque um V resolve nele pelo baixo. Mas um dominante nunca é
   tônica: a "resolução" V7→D7 é um elo de **cadeia de dominantes secundários** (V/V→V), não
   chegada à tônica.
2. **Inversão-como-tônica** (velhos-tempos): em `G7(#5)→Fm/C`, o código usa o **baixo** (`C`)
   como raiz da tônica mas a **qualidade** (`Fm`, menor) para o modo — cunhando "Dó menor" de
   um `Fá menor` invertido. `Fm/C` é o iv (subdominante menor emprestada), não a tônica.

O spec de `functional-analysis-baseline` já diz que o dominante resolve "**to a repose chord**" —
mas a implementação não impõe repouso. Esta change alinha a implementação ao spec e torna
"repose chord" **preciso**.

## What Changes

- **Guarda de REPOUSO** no `chediak_functional_center`: uma resolução só estabelece tônica se o
  acorde-alvo for de **repouso** (`Category` ≠ `DOMINANT` — sem trítono real). Alvo dominante-7 é
  rejeitado como candidato a tônica (é elo de cadeia secundária).
- **Guarda de RAIZ==BAIXO**: a tônica repousa na própria raiz — o alvo só conta como tônica se
  `root == bass`. Rejeita `Fm/C` (raiz `F`, baixo `C`). O modo segue vindo da qualidade do
  acorde de repouso, agora coerente (raiz==baixo garante que a qualidade é da raiz certa).
- **Efeito medido ao vivo** (verificado nesta sessão): corrige **velhos-tempos** (acha `G7(9)→C`,
  centro `C major`, que **concorda** com `detect_key`) e põe **a-ra** em quarentena honesta (em
  vez do `D major` errado).

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `functional-analysis-baseline`: o requisito "Tonal center is established by Chediak's
  functional criterion" passa a definir **repose chord** com precisão — o acorde-alvo da
  resolução deve ser não-dominante (sem trítono real) **e** ter `root == bass`; caso contrário
  não estabelece tônica (vira quarentena honesta).

## Impact

- **Código:** só
  `packages/harmonic_analysis/src/harmonic_analysis/validation/functional_center.py` (a função
  `chediak_functional_center`) + seus testes. **NÃO** toca `detect_key`, o motor de análise, o
  invariante funcional, nem a trava de trítono do 3b (que opera no caminho do motor, não no
  achador de corroboração).
- **Gate (zero-regressão + ganho):** re-rodar `scripts/songbook_baseline.py` — invariante
  funcional **continua 62/62** (intocado); concordância de centro **sobe ou se mantém** (era
  47/59 = 80%); **nenhuma música hoje concordante pode passar a divergir**. Cobertura pode cair
  levemente (mais quarentena honesta onde não há resolução a repouso num extremo) — isso é
  CORRETO: quarentena honesta > centro errado. Re-rodar `scripts/worklist_adjudication.py` — as
  5 divergências por dominante/inversão-como-tônica saem da worklist. `make test`/`make lint`.
- **Regra de ouro:** Cifra Club é só fonte; Chediak é a base; centro é **corroboração**, não
  acurácia; invariante a transposição; nunca reamarrar `cc_key`.
