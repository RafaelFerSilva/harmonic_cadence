# Worklist de corroboração — adjudicação (#7)

> **Chediak arbitra, não o detector.** Ledger de curadoria das divergências
> `detect_key × chediak_functional_center` sobre o songbook (`cifras/*.md`). Cada linha é um
> **fato musicológico adjudicado** pela teoria do Chediak aplicada às cadências visíveis (tônica =
> repouso; V = tensão; moldura estrutural 1º/último; casa diatônica) — **nunca** pela anotação do
> Cifra Club. Gerar a lista crua: `uv run python scripts/worklist_adjudication.py` (READ-ONLY);
> medir: `uv run python scripts/songbook_baseline.py`.
>
> **Não é placar do detector.** A divergência não penaliza nenhum método; a análise funcional é
> invariante a transposição e a tonalidade absoluta é só quadro de exibição. O motor fica **intacto**.

## Vereditos (n=170, adjudicado 2026-07-01 — 32 divergências)

| música | detect_key | funcional | **veredito (Chediak)** | acerta | conf | evidência decisiva |
|---|---|---|---|---|---|---|
| a-volta | ~~G maj~~ **C maj** ✔ | C maj | **Dó maior** — *resolvido pelo gate (Path C)* | agora concordam | alta | abre `C7M Am7 Dm7 G7 C7M` (I-vi-ii-V-I); detect pegava o **V** (`G7`); `add-cadential-v-as-tonic-path` corrige |
| atras-da-porta | ~~C# maj~~ **F# maj** ◐ | F# min | **Fá# menor** — *gate corrige a TÔNICA (F#), modo ainda maior* | parcial | alta | `C#7(b9)→F#m` = V→i; o Path C acerta a tônica; `_x_mode` vira maior por 1 acorde F# maior entre 9 menores (fora de escopo) |
| bom-de-viver | A min | D min | **Ré menor** (modula C/Am→Dm) | funcional | méd | fecha `A7(b13)→Dm7(9)` (V→i); detect pegou a área de abertura (Am) |
| chora-tua-tristeza | D maj | G maj | **Ré maior** | **detect** | alta | abre `D7M(9) D6` (tônica D nítida); funcional pegou o `G7M` tonicizado no meio (ii-V→IV) |
| ciume | E maj | D maj | **Ré maior** | funcional | alta | `Em7 A7 D6/9` = ii-V-I; detect pegou o **II7 secundário** (E7 = V/V) |
| dia-de-vitoria | ~~E maj~~ **A maj** ✔ | A maj | **Lá maior** — *resolvido pelo gate (Path C)* | agora concordam | méd-alta | abre `A(add9)`, `E7→A` (V-I); `add-cadential-v-as-tonic-path` corrige |
| inutil-paisagem | D min | A maj | **Lá maior** | funcional | méd-alta | cadeia `B7→E7→A7` pousa em A; Dm é iv-cliché emprestado |
| poema-azul | C maj | G maj | **Sol maior** | funcional | alta | 1º=`G7M`, últ=`G`, `D7→G7M` (V→I); detect pegou o **IV** (C) |
| razao-de-viver | G maj | D maj | **Ré maior** | funcional | média | `Em7 A7 D7M` = ii-V-I a repouso; G7/D7 são dominantes blues |
| enquanto-a-tristeza-nao-vem | C min | G min | **Dó menor** | **detect** | alta | abertura i-iv-bVII-bIII-bVI-V; `G7b9→Cm`; funcional pegou o **v** tonicizado no fim |
| nos-e-o-mar | D maj | D min | **Ré maior** | **detect** | alta | 1º **e** últ = `D7M` (moldura maior); `A7→Dm` do meio é modulação |
| imagem | G min | G maj | **Sol menor** | **detect** | média | termina `Gm7`, `D7b9→Gm` (V→i); funcional pegou um pivô G maior |
| eh-menina | D maj | E min | **Ré maior** | **detect** | média | fecha `A7→D7M(9)` (V-I a repouso maj7) + `D7M(9) Em7` (I-ii); funcional pegou o ii (Em) |
| gaiolas-abertas | C# maj | D# min | **Ré♭ maior** (=C#) | **detect** | alta | `Ebm7 Ab7 Db7M` = ii-V-I; detect=C#(=Db) é o **I**; funcional pegou o **ii** (Ebm) |
| canto-de-ossanha | C min | C maj | **Dó menor** | **detect** | alta | vamp `Cm Cm/Bb A° Ab6` abre/fecha; funcional pegou o `G7→C` maior da ponte |
| tema-do-boneco-de-palha | G min | A# maj | **Sol menor** | **detect** | alta | abre `Gm7 Gm6`, `Am7b5 D7b9 Gm(7M)` = ii-V-i; funcional pegou a relativa maior (Bb) |
| tempo-feliz | E min | A min | **Mi menor** | **detect** | méd-alta | vamp `Am6 B7b9 Em7` recorrente, fecha em `B7b9` (V de Em); funcional pegou o `E7→Am` |
| ligia | D# min | C# min | **Dó# menor** | funcional | média | abre/volta a `C#m7(9)`, `G#7(b13)→C#m` (V→i); detect pegou um área secundária (D#m) |
| tereza-da-praia | C# min | B maj | **Si maior** | funcional | média | `C#m7 F#7 B7M` = ii-V-I (B7M/B6 repouso); detect pegou o **ii** (C#m) |
| no-cordao-da-saideira | E maj | E min | **Mi menor** | funcional | alta | `Em(add9)` abre/fecha, `B7b9→Em` (V→i); detect trocou o modo |
| o-morro-nao-tem-vez | A maj | A min | **Lá menor** (vamp A7 modal) | funcional | média | `E7→Am7` (V→i); a vamp `A7(13) G7(13)` é bVII-I modal, não tônica maior |
| esperanca-perdida | D min | F maj | **Fá maior** | funcional | alta | abre `F7M`, fecha `F6`, `Gb7#11→F7M` (SubV→I); detect pegou a relativa menor |
| cancao-do-nosso-amor | C# min | A maj | **Lá maior** | funcional | média | `Bm7 E7 A` / `E7 A7M` = ii-V-I a A; detect pegou o **iii** (C#m) |
| maria-ninguem | A min | F maj | **modulante → Fá maior (fim)** | funcional (fraco) | baixa | círculo A/C/F; `C7→F7M` fecha em F |
| ah-se-eu-pudesse | F maj | E maj | **modulante → Mi maior (fim)** | funcional (fraco) | baixa | abre Eb maior, `F7#11→E7M` (SubV→I) fecha em E |
| bolinha-de-sabao | G maj | D min | **Dó maior** — *nenhum dos dois* | armadilha ii-V | média | `Dm7 G7 → C9 / C7M`; detect pegou o **V** (G7), funcional o **ii** (Dm7); o I (C) é a tônica |
| menina | G maj | D min | **Dó maior** — *nenhum dos dois* | armadilha ii-V | média | `Dm7 G7 C7M` = ii-V-I; detect pegou o V, funcional o ii — nenhum pegou o I (C) |
| rio | C maj | G min | **Fá maior** — *nenhum dos dois* | armadilha ii-V | média | `Gm7 C7 → F7M` = ii-V-I; detect pegou o **V** (C7), funcional o **ii** (Gm7); o I é F |
| cartao-de-visita | D maj | B min | **relativo-ambíguo D/Bm** (~Ré maior) | detect (fraco) | baixa | `Em7 A7 D9` recorre (ii-V a D), mas `F#7→Bm7` também; relativa genuína |
| embarcacao | D# maj | G# min | **modulante** (sequência ½t) | — | baixa | 84 acordes; a 2ª metade é a 1ª transposta ½t acima; sem tônica única |
| eu-te-amo | D min | B maj | **modulante** (cromático) | — | baixa | descida cromática por muitas tonalidades; fecha `C7(SubV)→B7M` |
| o-amor-e-chama | B maj | D# maj | **modulante** (sequência) | — | baixa | vamp `Em7 Bm7`, depois desce F#7M→E7M→Eb7M→D7M; sem tônica única |

## Leitura (o achado, atualizado n=170)

As 32 divergências **não têm um vencedor único** — cada método falha de um jeito, e apareceu um
**terceiro modo de falha**:

- **Funcional certo / `detect_key` errou (14)** — o K-S agarra o **V**, o **IV**, o **ii**, o
  **iii** ou a **relativa**: o discriminador estatístico perde para a densidade de dominantes
  secundários e ii-V da MPB. O critério funcional (V→I limpo a repouso, pp.84/87) acerta.
- **`detect_key` certo / funcional errou (9)** — o achador funcional agarra um **v/ii/pivô
  tonicizado localmente** num extremo estrutural (último acorde, ou uma cadência secundária),
  ignorando a moldura de abertura e a casa diatônica global.
- **NOVO — armadilha do ii-V: nenhum dos dois (3)** — `bolinha-de-sabao`, `menina`, `rio`: a
  música é um vamp de **ii-V** (`Dm7 G7`, `Gm7 C7`), o **I** (C, F) está presente como repouso,
  mas o `detect_key` pega o **V** e o funcional pega o **ii** — nenhum pega a tônica. É o caso mais
  instrutivo: mostra que a tônica pode estar sub-representada face ao movimento ii-V.
- **Modulantes / baixa confiança (6)** — sem tônica global única; a resposta pende para o fim
  (`ah-se-eu-pudesse`, `maria-ninguem`, `cartao-de-visita`, `embarcacao`, `eu-te-amo`,
  `o-amor-e-chama`).

**Consequência de projeto:** continua **não havendo regra-cega segura** (funcional 14, detect 9,
nenhum 3, modulante 6). A worklist é **curadoria**, não placar.

**Gate cirúrgico entregue (`add-cadential-v-as-tonic-path`, Path C):** o subconjunto alta-confiança
de V-como-tônica **cadenciado na abertura** foi automatizado — `a-volta` (G→C) e `dia-de-vitoria`
(E→A) agora **concordam** (concordância 121→123), `atras-da-porta` teve a **tônica** corrigida
(F#, modo ainda maior). Guardas Chediak: ≥2 resoluções V→X, X=1º acorde, a peça não fecha em Y como
repouso. **Zero regressão** (4 gates 170/170, nenhuma concordância perdida; Paths A/B intactos).
O restante fica na curadoria: as outras geometrias (K-S pega IV/ii/iii/relativa) e a **armadilha do
ii-V** (o achador funcional preferir o **alvo do V** (o I) ao **ii**) são frentes futuras.
