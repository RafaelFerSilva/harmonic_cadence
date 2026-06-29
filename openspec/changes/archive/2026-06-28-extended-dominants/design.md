## Context

As changes XVIII (`dominant-auxiliary-and-secondary-subv`) e XIX (`ii-cadential-secondary-auxiliary`)
classificaram dominantes e o II cadencial pelo **alvo da resolução** (diatônico=secundário,
empréstimo=auxiliar). Chediak XXVIII (pp.107-108, lida do scan, offset 0) acrescenta o eixo
que falta: quando o alvo é **outro dominante**, o acorde é **estendido** — pertence à cadeia,
não à tonalidade — e por isso **não leva número romano** (escala-acorde mixolídio).

Hoje, em `harmony.py`, o ramo de dominante (`if chord.is_dominant_seventh:`, ~L122) chega no
sub-ramo `Dsec` (~L177-188): `ni == 5 and not target_is_tonic` → `Dsec V7/{grau}`. Para
`A7→D7`, `D` é o grau II, então `A7` vira `Dsec V7/II` — o número romano que Chediak nega.
E `roman.py` (~L86-90) devolve `V7/{degree}` para **qualquer** dominante-7 seguido de acorde.

Camada de função + cifra analítica; **não toca** `detect_key` → baseline idêntico. A trava é
a suíte: `A7→D7` muda de `Dsec`/`V7/II` para `Dext`/sem-grau.

**Sondagem ao vivo (antes de codar, C maior):**
- `A7 D7 G7 C` → `A7`=`Dsec V7/II`, `D7`=`Dsec V7/V`, `G7`=`D V7`, `C`=`T`. Confirma o
  buraco: `A7`/`D7` (que resolvem em outro dominante por 4ªJ) recebem grau; o elo final `G7`
  (alvo tônica) e `C` já estão certos.
- `F7 E7 Eb7 D7` → `F7`=`SD IV7 blues`, `E7`=`T III7`, `Eb7`=`SubV`, `D7`=`SD II7`. **Achado
  que estreitou o escopo:** o ramo de blues I7/IV7 (Chediak XXXIV) captura `F7`/`E7` antes —
  um par de **semitom** local é indistinguível de um IV7→III7 de blues. Os exemplos de SubV
  estendido do Chediak (p.107c) são cadeias cromáticas longas (`F#7 F7 E7 Eb7 D7 Db7 C`); a
  desambiguação exige detecção de **cadeia** (≥2 elos), não de par. Logo o SubV estendido
  (XXVIII c/d) sai desta change. O caso **4ªJ ascendente** não tem leitura concorrente (um
  dominante que sobe 4ªJ para outro dominante *é* o estendido do ciclo de quintas) → seguro.

## Goals / Non-Goals

**Goals:**
- Reconhecer o dominante estendido (dominante → dominante, por **4ªJ ascendente**) e
  classificá-lo `Dext`, escala-acorde mixolídio.
- Suprimir o numeral aplicado (`V7/x`) do dominante estendido (fiel a Chediak).
- Tirar o `A7→D7` de `Dsec V7/II`.

**Non-Goals:**
- **SubV estendido por semitom (XXVIII c/d)** — colide com a leitura de blues no par local
  (ver Context); exige detecção de cadeia cromática (≥2 elos). **Change própria.**
- Distinção **gráfica** de seta cheia vs colchete de cadeia dos II V's — é apresentação,
  fora da camada de função.
- Ramo próprio para o `iim7` antes do elo estendido — segue o `D2` (II cadencial) existente;
  os II V's estendidos emergem por composição (`D2` + `Dext`).
- Acordes interpolados (XXIX) — change futura.
- Tocar `detect_key`/`_tritone_gate`/parsing.

## Decisions

### D1 — Detecção: dominante cujo PRÓXIMO acorde é dominante a 4ªJ acima

Um sub-ramo novo dentro do bloco `chord.is_dominant_seventh`, **antes** de `Dsec`:
`next_chord is not None and next_chord.is_dominant_seventh` e `_get_interval(chord.root,
next.root) == 5` (4ªJ ascendente). *Por quê só 4ªJ:* a sondagem mostrou que o caso semitom
colide com blues no par local (Context); o caso 4ªJ é inambíguo. *Por quê só olhar 1 acorde à
frente:* a definição é local — "resolve em outro dominante" — então o vizinho imediato basta;
não preciso varrer a cadeia nem mudar a assinatura de `analyze_function`.

### D2 — Precedência sobre `Dsec`/`Daux`/`SubV`

O sub-ramo `Dext` vem **antes** dos ramos de alvo (`Dsec` em ~L177, `Daux` em ~L153, `SubV
secundário` em ~L138). *Por quê:* `Dsec` dispara em `ni == 5 and not target_is_tonic` e
capturaria `A7→D7` como `V7/II`; a qualidade-dominante do alvo é o discriminador que separa
estendido de secundário, então tem de ser testada primeiro. O elo final da cadeia (`G7→C`,
alvo tônica; ou `D7→G` quando `G` é diatônico não-dominante) **não** casa o sub-ramo (o
próximo não é dominante) e segue para `D`/`Dsec` — exatamente o "reconecta à tonalidade".

### D3 — Código de função `Dext`

Novo código `Dext` em `FunctionCode` (harmony.py L19-22) e em `HARMONIC_FUNCTIONS`
(constants.py), nome "Dominante Estendido", descrição citando Chediak pp.107-108, escala-acorde
mixolídio. *Por quê um código próprio:* é uma função distinta de `Dsec` (não atrelada à
tonalidade); um código separado é o que permite a `roman.py` suprimir o numeral e os relatórios
distinguirem o estendido. O futuro SubV estendido (semitom) poderá reusar `Dext` com o sabor no
nome quando vier na sua change.

### D4 — Supressão do numeral em `roman.py`

`roman_numeral` (roman.py ~L86): antes de devolver `V7/{degree}`, se `next_chord` é dominante a
**4ªJ acima** (`_get_interval(chord.root, next.root) == 5`), devolver a **cifra simples** do
acorde (sem `V7/x`). *Por quê em roman.py e não só na função:* o numeral é responsabilidade da
camada roman; a função (`Dext`) e a cifra (sem grau) são as duas faces da mesma regra do Chediak,
e a spec `roman-numeral-analysis` exige a notação fiel. Mantém `roman.py` como única fonte do
numeral. *Por quê repetir o teste de intervalo aqui (e não ler o código de função):* `roman.py`
não recebe a classificação de função; computar a relação local mantém as camadas desacopladas.

### D5 — Mixolídio para o estendido: threading de `next_chord` (escolha A)

A sondagem mostrou que a regra **posicional** (Chediak p.113) manda um `II7` estendido (ex. `D7`
na cadeia) para **lídio b7**, contradizendo XXVIII (p.339: estendido = mixolídio). XXVIII é a
regra mais específica → vence. Implementação: `recommended_scale`/`analyze_chord` ganham
`next_chord` opcional; quando o acorde é um dominante estendido (próximo é dominante 4ªJ acima),
força mixolídio — **sobre o default posicional**, mas **não** sobre o dominante alterado (a
alteração demanda sua escala). `analysis_service` passa o próximo acorde via `enumerate`. *Por
quê não ler o código de função:* `chord_scale` não recebe a classificação; recomputar a relação
local mantém a camada de escala desacoplada (mesmo princípio do D4). Toca a capability
`chord-scale-tensions` (+1 spec delta).

## Risks / Trade-offs

- **[`A7→D7` muda de `Dsec V7/II` para `Dext`]** → é a leitura fiel (Chediak: estendido não leva
  grau). A trava é a suíte; reviso testes que codificavam `V7/II` para esse padrão.
- **[Falso estendido: dois dominantes adjacentes sem cadeia real]** → a conjunção é estrita
  (dominante→dominante por 4ªJ asc OU semitom desc); um par de dominantes sem essa relação de
  intervalo não casa. Aceitável; é a melhor leitura local sem metro.
- **[Elo final ambíguo]** → o último dominante da cadeia resolve num não-dominante e cai em
  `D`/`Dsec` por construção (não casa o sub-ramo). Coberto por cenário de spec.
- **[Baseline]** → impossível regredir (`detect_key` intacto); rodo `scripts/key_baseline.py`
  como sanidade.

## Migration Plan

1. Adicionar `Dext` ao `FunctionCode` e `HARMONIC_FUNCTIONS` (constants.py).
2. Inserir o sub-ramo `Dext` no bloco de dominante, **antes** de `Dsec`/`Daux`/`SubV`.
3. Suprimir o `V7/x` em `roman.py` quando o próximo acorde é dominante de cadeia.
4. Testes: dominante estendido (`A7 D7`), cadeia (`A7 D7 G7 C` — `G7`=`D`), guard secundário
   (`E7 Am`=`Dsec V7/vi`), e o numeral suprimido.
5. `make test` + `make lint`; `scripts/key_baseline.py` (idêntico). Atualizar ROADMAP/AGENTS.
6. Rollback = remover o sub-ramo + a guarda do `roman.py` + a entrada `Dext`.

## Open Questions

- O elo final que resolve num **empréstimo** (não-dominante, não-diatônico) — ex. cadeia que
  termina num `Daux` — deve ser o último `Dext` ou já o `Daux`? Decisão: o critério é "próximo é
  dominante"; um alvo de empréstimo não-dominante encerra a cadeia (vira `Daux`). Refinável se a
  sondagem ao vivo achar contraexemplo no corpus.
