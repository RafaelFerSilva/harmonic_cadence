## 1. Trava (antes de tocar código)

- [x] 1.1 Rodar `make test` e registrar a contagem verde (referência da suíte).
- [x] 1.2 Anotar o comportamento atual (sondagem): `Bb7→Eb`→Emp bVII7; `Eb7→Ab`→V7/None; `Ab7→G`→Emp bVI7; `Eb7→Dm`→Emp; controles `E7→Am`/`D7→G`/`Db7→C`→ corretos.

## 2. Infra (constants + helper)

- [x] 2.1 Adicionar `Daux` ao `FunctionCode` (Literal) e a `HARMONIC_FUNCTIONS` em `constants.py` (nome "Dominante auxiliar", descrição citando Chediak p.99).
- [x] 2.2 Helper `_chromatic_degree(target_root)` em `harmony.py`: offset da tônica → grau com bemol (bII, bIII, bVI, bVII…), para o rótulo `V7/<grau>`.

## 3. Reorganização do ramo de dominante (harmony.py)

- [x] 3.1 Mover I7(pos0)/IV7(pos5) blues para o topo do ramo (intocados, Chediak XXXIV).
- [x] 3.2 Inserir, com `next_chord`, ANTES de `bVII7`/`bVI7` Emp: **SubV7 secundário** (`_get_interval(next.root, chord.root)==1` e alvo diatônico não-tônica → `SubV`, "SubV7 secundário (SubV7/{grau})") e **dominante auxiliar** (`ni==5`, alvo não-tônica e `get_degree(next)` None → `Daux`, "Dominante auxiliar (V7/{grau cromático})").
- [x] 3.3 Manter `bVII7`/`bVI7` Emp (pos 10/8) DEPOIS — alcançado só quando não houve resolução (`Bb7→C`).
- [x] 3.4 Manter, como hoje, o V7/x secundário (`ni==5`, alvo diatônico), VII7 cadencial, e o SubV primário (`bII7`).

## 4. Testes

- [x] 4.1 Auxiliar: `Bb7→Eb` → `Daux` "V7/bIII"; `Eb7→Ab` → `Daux` "V7/bVI".
- [x] 4.2 SubV7 secundário: `Ab7→G` → `SubV` "SubV7/V"; `Eb7→Dm` → `SubV` "SubV7/ii".
- [x] 4.3 Invariantes: `E7→Am`→Dsec V7/vi; `D7→G`→Dsec V7/V; `Db7→C`→SubV primário; `G7→C`→D; `C7→G`→não-Dsec (blues); `Bb7→C`→Emp bVII7.
- [x] 4.4 Nenhum desses dominantes vira `V7/None`.

## 5. Quality gate + docs

- [x] 5.1 `make test` verde; `make lint` limpo.
- [x] 5.2 `scripts/key_baseline.py` ao vivo: baseline **idêntico** (não toca `detect_key`).
- [x] 5.3 Atualizar `ROADMAP.md` (dominante auxiliar + SubV7 secundário, Chediak XVIII p.99; próxima = II cadencial XIX).
- [x] 5.4 `openspec validate dominant-auxiliary-and-secondary-subv --strict` passa; pronto para `openspec archive`.
