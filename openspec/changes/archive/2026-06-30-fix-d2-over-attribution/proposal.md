## Why

O código `D2` (II cadencial, Chediak XIX p.100) é **super-atribuído**. O ramo 0e de
`HarmonicAnalysis.analyze_function` ([harmony.py:293-318]) dispara quando: o acorde é menor +
o **próximo** acorde é dominante-7 **por qualidade** (`is_dominant_seventh`) + intervalo de 4ªJ
ascendente — **sem checar se o próximo acorde FUNCIONA como dominante**. Um probe ao vivo (n=62)
mediu **~168 incoerências `D2`→não-dominante** em 46/62 músicas: **70 `D2→SD`, 57 `D2→T`, 34
`D2→Emp`, 7 `Outro`**.

Causa-raiz: o "V" que o `D2` supostamente prepara é, na verdade, um **I7 de blues** (pos 0 → `T`),
um **IV7 de blues** (pos 5 → `SD`), ou um **empréstimo modal não-resolvente** (bVII7/bVI7 → `Emp`).
Ex.: a-ra em Sol maior, `Dm7 G7` repetido — o motor chama `Dm7` de "ii cadencial" mas coda `G7`
como `T` (I7 blues). Chediak XIX amarra o ii cadencial a **preparar um dominante FUNCIONAL**, não
um acorde de qualidade-dominante. O próprio motor já distingue esses casos no bloco
`if chord.is_dominant_seventh` ([harmony.py:128+]) — o ramo 0e só não consulta essa lógica.

## What Changes

- **O `D2` só é emitido se o dominante seguinte RESOLVER no seu alvo** — um ii cadencial prepara
  um dominante, e um dominante só funciona quando resolve por 4ªJ descendente. Teste preciso e
  **puramente intervalar** (transposição-invariante, independe do tom e do código do V): com o V
  no índice `i+1` e `alvo = (Vroot + 5) % 12`, o acorde em `i+2` deve ter raiz (ou baixo) == alvo;
  senão o V não funciona como dominante (é um blues `I7`/`IV7` ou empréstimo não-resolvente) e o
  menor **não** é II cadencial. Isto é melhor que checar o código do V — o ramo de blues coda
  `I7`/`IV7` (pos 0/5) como `T`/`SD` **antes** de considerar resolução, então um `F7→Bb` legítimo
  (auxiliar) ficaria mascarado; o teste de resolução não cai nessa armadilha.
- **Medição (probe ao vivo, n=62):** dos **363** `D2` emitidos, **199 resolvem** (legítimos) e
  **164 não resolvem** (over-attribution — ex.: a-ra `Dm7 G7→Dm7`, o `G7` não vai a `C`). A fix
  zera os 164 e preserva os 199 (incl. `Em7 A7→D7` ii-V secundário e `Gm7 C7→F7M`).
- **NÃO-ESCOPO:** consertar a detecção de tom; gatear o invariante ii-V no baseline (fica para
  depois que a contagem de não-resolventes chegar a 0).

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `harmonic-function`: o requisito "II cadential chord classified by its dominant's target" ganha
  a **pré-condição de resolução** — o dominante seguinte deve resolver no seu alvo (o acorde em
  `i+2` baixa em `(Vroot+5)%12`); senão o acorde menor não é II cadencial.

## Impact

- **Código:** só `packages/harmonic_analysis/src/harmonic_analysis/domain/harmony.py` (ramo 0e do
  `analyze_function`, + helper se preciso). `analyze_function` é fonte única (consumida por
  `formatter.py:80` e `analysis_service.py:198`) — a guarda beneficia os dois call sites. NÃO
  toca `detect_key`, `chediak_functional_center`, nem o gate do baseline.
- **Gate (zero-regressão + ganho):** probe de `D2` sobre `cifras/*.md` — `D2` não-resolventes
  caem de **164 → 0**; os **199** resolventes (legítimos) permanecem `D2`. Os invariantes do
  baseline (trítono 62/62, diminuto 62/62) não regridem (a fix só muda menor↔D2, não toca dom-7
  nem diminuto). `make test` verde (ajustar testes que codificavam o `D2` antigo, documentando),
  `make lint` limpo. Os acordes que perdem o `D2` caem na função diatônica/outra — correto.
- **Regra de ouro:** Chediak é a base (XIX p.100 — ii cadencial prepara dominante FUNCIONAL);
  invariante a transposição; medir contra o baseline ao vivo; nunca reamarrar `cc_key`.
