# Worklist de corroboração — adjudicação (#7)

> **Chediak arbitra, não o detector.** Este é o ledger de curadoria das divergências
> `detect_key × chediak_functional_center` sobre o songbook (`cifras/*.md`). Cada linha é um
> **fato musicológico adjudicado** pela teoria do Chediak aplicada às cadências visíveis (tônica =
> repouso; V = tensão; moldura estrutural 1º/último; casa diatônica) — **nunca** pela anotação do
> Cifra Club. Gerar a lista crua: `uv run python scripts/worklist_adjudication.py` (READ-ONLY);
> medir: `uv run python scripts/songbook_baseline.py`.
>
> **Não é placar do detector.** A divergência não penaliza nenhum método; a análise funcional é
> invariante a transposição e a tonalidade absoluta é só quadro de exibição.

## Vereditos (n=10, adjudicado 2026-07-01)

| música | detect_key | funcional | **veredito (Chediak)** | acerta | confiança | evidência decisiva |
|---|---|---|---|---|---|---|
| atras-da-porta | C# maj | F# min | **Fá# menor** | funcional | alta | `C#7(b9)→F#m` = V→i; `detect` pegou o **V** (C#) — V-como-tônica |
| ciume | E maj | D maj | **Ré maior** | funcional | alta | `Em7 A7 D6/9` = ii-V-I limpo; `detect` pegou o **II7 secundário** (E7 = V/V) |
| poema-azul | C maj | G maj | **Sol maior** | funcional | alta | 1º=`G7M`, últ=`G`, `D7→G7M` (V→I); `detect` pegou o **IV** (C) |
| inutil-paisagem | D min | A maj | **Lá maior** | funcional | méd-alta | cadeia de dominantes `B7→E7→A7` pousa em A; `E7→A`; Dm é iv-cliché emprestado |
| razao-de-viver | G maj | D maj | **Ré maior** | funcional | média | `Em7 A7 D7M` = ii-V-I a repouso (`D7M`); `G7`/`D7` são dominantes blues |
| enquanto-a-tristeza-nao-vem | C min | G min | **Dó menor** | **detect** | alta | abertura i-iv-bVII-bIII-bVI-V(#5) é Cm puro; `G7b9→Cm`; funcional pegou o **v** tonicizado no fim (`D7→Gm`) |
| nos-e-o-mar | D maj | D min | **Ré maior** | **detect** | alta | 1º **e** último = `D7M` (moldura maior); `A7→Dm` do meio é modulação; funcional pegou o meio |
| imagem | G min | G maj | **Sol menor** | **detect** | média | termina `Gm7`, `D7b9→Gm` (V→i); funcional pegou um pivô G maior no meio |
| maria-ninguem | A min | F maj | **modulante → Fá maior (tônica final)** | funcional (fraco) | baixa | peça em círculo (áreas A/C/F); `C7→F7M` fecha em F |
| ah-se-eu-pudesse | F maj | E maj | **modulante → Mi maior (tônica final)** | funcional (fraco) | baixa | abre em Eb maior (`Fm7 Bb7 Eb7M`), vagueia; `F7#11→E7M` (SubV→I) fecha em E |

## Leitura (o achado)

As divergências **se dividem ~meio a meio**, e cada lado revela uma fraqueza real e **oposta**:

- **Funcional certo / `detect_key` errou (5)** — `atras-da-porta`, `ciume`, `poema-azul`,
  `inutil-paisagem`, `razao-de-viver`. O K-S do `detect_key` agarra o **V**, o **IV** ou um
  **dominante secundário**: o discriminador estatístico perde para a densidade de dominantes
  secundários da MPB (a mesma lição da trava de trítono do 3b). O critério funcional (V→I limpo a
  repouso, Chediak pp.84/87) acerta a tônica.
- **`detect_key` certo / funcional errou (3)** — `enquanto`, `nos-e-o-mar`, `imagem`. O achador
  funcional agarra um **v/pivô tonicizado localmente num extremo estrutural** (o último acorde),
  ignorando a moldura de abertura e a casa diatônica global.
- **Genuinamente modulantes (2)** — `ah-se-eu-pudesse`, `maria-ninguem`: sem tônica global única;
  a tônica **final** pende para a resposta do funcional.

**Consequência de projeto:** **não há regra-cega segura.** Um gate ingênuo "confie no funcional
sobre o `detect_key`" regrediria os 3 casos onde o `detect_key` está certo. Isso **valida** manter
a worklist como curadoria (o Chediak adjudica), não como placar — exatamente a regra de ouro. Um
gate futuro para o `detect_key` teria de ser **cirúrgico** (só os casos alta-confiança de
V-como-tônica: `atras-da-porta`, `ciume`), com guarda que **não toque** os 3 detect-certo e prove
zero regressão contra o baseline funcional ao vivo.
