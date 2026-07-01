## Why

O detector de cadências (`analyze_cadences`, [cadence.py]) classifica a família autêntica
(perfeita/imperfeita/autêntica) por **posição de grau** — `degree_base(degree_seq[i])` —
**ignorando a FUNÇÃO** que o coder atribuiu ao alvo. Resultado: ele rotula `V→I` como cadência
mesmo quando o motor já decidiu que o "I" **funciona** como dominante (`D2`, ii cadencial) ou
diminuto (`Dim`). Probe ao vivo (n=62): **5 músicas** com a incoerência — `ah-se-eu-pudesse`
(`C7(9)→Fm7` = D2), `ate-parece` (`B7(b9)→Em7` = D2), `avarandado` (`E7(9)→A°` = Dim),
`enquanto-a-tristeza-nao-vem` (`G7(b9)→Cm7` = D2), `so-tinha-de-ser-com-voce` (`C7(b9)→Fm7(9)` =
D2).

Causa-raiz: Chediak define a cadência pela **combinação de funções "D" e "T"** (Vol. I, XXXII,
p.110 — *"Cadência imperfeita: é o resultado da combinação 'D' e 'T'..."*), não pelo grau. Quando
o alvo `V→I`-por-grau funciona como `D2`/`Dim`, ele **não é repouso (T)**: é o ii de uma
tonicização (ou um diminuto de passagem). Chediak XXXIII (*Resolução direta*, p.111) mostra
exatamente isso — `Em7 A7 | Dm7 G7 | C7M`: um dominante resolvendo num acorde que é ele mesmo um
ii (`Dm7`) é **resolução direta V7/II→IIm**, um elo de cadeia, **não uma cadência**. O detector
erra porque só vê o grau global, não a função.

## What Changes

- **A família autêntica (perfeita/imperfeita/autêntica) e a plagal só são emitidas se o alvo
  FUNCIONAR como repouso.** `analyze_cadences` passa a receber os `function_codes` (a saída do
  coder, alinhada por índice) e, nos ramos que resolvem na tônica (`b == "I"`), suprime a
  classificação quando o alvo carrega uma função **não-repouso** — dominante (`D`, `D2`, `Dsec`,
  `Daux`, `Dext`) ou SubV (`SubV`, `Sub2`) ou diminuto (`Dim`). Esses pares são **resolução
  direta (XXXIII)**, elos de cadeia de ii-V/dominantes secundários, não punctuação de frase — são
  **suprimidos**, não reclassificados como deceptiva (a deceptiva é um evento cadencial; um elo de
  cadeia não é).
- **Backward-compatible:** `function_codes` é opcional; sem ele, o comportamento (grau-puro) é
  idêntico — os testes da taxonomia e os call sites legados seguem verdes.
- **Gate de coerência no baseline:** o `songbook_baseline.py` ganha um terceiro invariante
  funcional gateado — **nenhuma cadência da família autêntica/plagal tem alvo de função
  dominante/diminuta**. Nasce **VERDE** (as 5 incoerências viram 0 pós-fix). Fecha a frente #6.
- **NÃO-ESCOPO:** consertar a detecção de tom ou o coder de função (o `D2`/`Dim` do alvo está
  **correto** — o erro é a cadência ignorá-lo); mexer na meia-cadência ou na deceptiva (não
  resolvem na tônica, sem requisito de repouso).

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `harmonic-cadence`: a família autêntica/plagal ganha a **pré-condição de função de repouso** no
  alvo — uma cadência só resolve na tônica quando o "I" **funciona** como T (não como dominante,
  SubV ou diminuto); senão é resolução direta (XXXIII), não cadência.
- `functional-analysis-baseline`: a coerência cadência×função **deixa de ser deferida** e passa a
  ser um invariante gateado (alvo de cadência autêntica/plagal nunca é função dominante/diminuta).

## Impact

- **Código:** `domain/cadence.py` (novo param + guarda nos ramos `b == "I"`);
  `services/analysis_service.py` (mover o `_detailed_harmonic_analysis` para ANTES da cadência e
  passar os `function_code`s); `scripts/songbook_baseline.py` (novo gate). NÃO toca o coder de
  função, o `detect_key` nem o pré-passe do `D2`.
- **Gate (zero-regressão + ganho):** as 5 incoerências `V→I`-com-alvo-`D2`/`Dim` somem das
  cadências; nenhuma cadência legítima (alvo função T) é removida. Invariantes do baseline
  (trítono 62/62, diminuto 62/62, D2 62/62) intactos; coerência de cadência nasce 62/62.
- **Regra de ouro:** Chediak é a base (XXXII p.110 — cadência = combinação D+T; XXXIII p.111 —
  resolução direta não é cadência); invariante a transposição (a guarda é por **função**, não por
  tom); medir contra o baseline ao vivo; nunca reamarrar `cc_key`.
