# Design — Parsing estruturado de acorde (fonte: Chediak Vol. I)

## Contexto e fonte de autoridade

A notação do corpus (Cifra Club) é a **sistemática Chediak**, cujo propósito
declarado é *"unificar a cifra em nosso país"* (Vol. I, folha de rosto). Usamos
o livro como **árbitro das convenções** — destilando fatos, em nossas palavras;
o texto, as tabelas como diagramadas e as 70 análises de músicas (PARTE 4) não
são copiados nem ingeridos. Páginas de referência (numeração impressa = física
no PDF; offset 0): **76, 77, 78, 79–81, 82, 84–85, 105**.

## O problema: três responsabilidades fundidas e duplicadas

O que hoje parece "detectar acorde" são três coisas distintas, embaralhadas em
dois motores que se ignoram:

```
  "G9" / "A7(13-)"
     │  ① PARSING (sintaxe)        key-free   →  hoje: duplicado em 2 lugares
     │  ② REALIZAÇÃO (pitch-classes) key-free  →  hoje: chord_realize (perde rótulo)
     │  ③ CLASSIFICAÇÃO (rótulo)     key-free  →  hoje: Chord (perde pitch-classes)
     ═══ a costura ═══
     │  ④ INTERPRETAÇÃO (grau, função)  key-bound → HarmonicAnalysis (fica onde está)
```

`substring-sniffing é estruturalmente impossível de acertar`: `C7(#9)` conta a
9 **e** a #9 porque `"9"` está dentro de `"#9"`. A correção exige **tokenizar**,
não testar `contains()`.

## Decisão: um parse estruturado por *slots*, com pitch-classes derivados

Uma `enum quality` não representa o domínio (`Csus4` não é "maior nem menor";
`C7(#11)` precisa de 5ª justa **e** #11). O acorde é um vetor de slots
independentes por grau, dos quais a realização e a categoria são derivadas:

```
ParsedChord
├── root      : Note                       # soletrada (C, Bb, F#) — não "A#"
├── bass      : Note | None                # só quando é nota real (resolve o /9)
├── third     : M3 | m3 | sus2 | sus4 | OMIT     # sus e power vivem AQUI
├── fifth     : P5  | dim5 | aug5                 # b5/#5 alteram o slot, não viram tensão
├── seventh   : NONE | m7 | M7 | dim7             # "dominante" = M3 + m7 (derivado)
├── added     : {6}                          # tons add (NÃO implicam 7ª): 6, add9
├── tensions  : {b9,9,#9,11,#11,b13,13}          # estrutura superior (implica 7ª)
└── pitch_classes : frozenset[int]           # DERIVADO — verdade sonora
```

Dois níveis porque os **pcs perdem função**: `b5` e `#11` colidem na mesma
classe; `Caug` é simétrico; `Cdim7 ≡ Ebdim7` no conjunto. Os *slots* nomeiam
(lossless quanto ao símbolo); os *pcs* soam. O parser produz os slots;
`realize()` deriva os pcs — **uma fonte, duas vistas**.

### Realização e *voicing* (Chediak pág. 78)

A cifra **não** estabelece *voicing*, ordem, dobramentos nem supressões: *"a
fundamental só pode ser suprimida se outro instrumento tocar o baixo; o
dobramento da terça deve ser evitado; pode-se suprimir a quinta justa"*. Logo
`pitch_classes` é o **conteúdo implícito canônico**, não o que é literalmente
tocado. A 5ª é omissível; os tons essenciais são fundamental, 3ª, 7ª e tensões.
O baixo invertido **entra** no conjunto (pág. 77: `C/Bb` = 1, 3M, 7m no baixo).

## Categoria (Chediak pág. 84–85) ⟶ derivada dos slots

Chediak usa **quatro categorias**, mais enxutas que nossa enum de 7 valores:

| Categoria | Definição (Chediak) | Derivação dos slots |
| --- | --- | --- |
| maior | 3M, 5J, **nunca 7m** (inclui `C`, `C7M`, `C6`) | third=M3 ∧ seventh∈{NONE,M7} |
| menor | 3m, 5J (inclui `Cm`, `Cm7`, `Cm7M`) | third=m3 ∧ fifth=P5 |
| sétima da dominante | **trítono 3M–7m** | third=M3 ∧ seventh=m7 |
| sétima diminuta | 3m, 5dim, 7dim (dois trítonos) | third=m3 ∧ fifth=dim5 ∧ seventh=dim7 |

`aug` e `m7b5` **não são categorias** — são variantes (quinta alterada). A enum
legada (`quality: str`) dos ~8 consumidores continua existindo, **derivada** dos
slots, agora expondo `suspended`/`power` que hoje somem em `major`.

## Os dois dialetos de notação

A tabela canônica (pág. 76) usa **`#/b`**; o corpus Cifra Club usa **`±`**. Os
dois coexistem no ecossistema BR — o parser aceita ambos e normaliza:

| Cifra Club | Chediak | grau |
| --- | --- | --- |
| `5+` `5-` | `#5` `b5` | quinta |
| `9+` `9-` | `#9` `b9` | nona |
| `11+` | `#11` | décima primeira |
| `13-` | `b13` | décima terceira |
| `2-` | `b9` | nona menor (Chediak: *"usa-se nona ao invés de segunda"*) |

Equivalência de classe de grau (pág. 76): `4≡11`, `6≡13`, `b6≡b13`, `2≡9`.

## Os três forks — resolvidos pela fonte

| Fork | Decisão | Citação |
| --- | --- | --- |
| `°` nu = tríade ou dim7? | **dim7** (tétrade 1, 3m, 5dim, 7dim) | pág. 77 (ex. `C°`) e 85 (categoria de 7ª diminuta) |
| `(4)` sobre 7ª = sus4 ou #11? | **sus4** (`V7/4` = "sétima com quarta suspensa"; o 4 suspende a 3ª) | pág. 105 |
| `2` nu = sus2 ou add9? | **add9** (9ª acrescentada, **3ª mantida**) — Chediak não tem `2` nem "sus2"; `2≡9` e o `add9` mantém a 3ª. *Sem fonte para sus2.* | pp. 76, 79 |

**Assimetria sourced (não arbitrária):** `4` nu → **sus4** (Chediak formaliza `V7/4`,
pág. 105), mas `2` nu → **add9** (Chediak não tem sus2). **Divergência registrada:**
o Cifra Club às vezes toca `B2` como sus2 (3ª omitida) — se um dia houver evidência
de corpus por música, pode sobrepor caso a caso; o default segue Chediak.

`add` vs extensão (pág. 79, 81): `C(add9)` = tríade + 9 **sem 7ª**; `C6/9` =
"Dó com sexta e nona" sem 7ª; um acorde de 6ª **bloqueia** o slot da 7ª.

## A regra seventh × tensions (parte sutil)

```
FASE 1 — RESOLVER O SLOT DA SÉTIMA (prioridade decrescente)
   7M / maj → M7 │ ° / dim → dim7 │ 6 presente → NONE (bloqueia) │ 7 → m7
   │ 9/11/13 nu → m7 implícita (M7 se houver maj/7M) │ senão → NONE
FASE 2 — PAPEL DE CADA NÚMERO (decidido pela ocupação dos slots)
   2 → add9: 9ª, 3ª mantida (sem 7ª) | 9 (com 7ª)   4 → sus4 (mesmo com 7ª → 7sus4)
   5± → slot da QUINTA (não é tensão)   6 → 6ª add (bloqueia 7ª) | 13 (com 7ª)
   9/11/13 → tensão no grau (± = acidente)
```

`5` e `4` **não são tensões**: `5±` muta a quinta, `4` muta a terça (sus). Só
`9/11/13` (e `6` sobre 7ª) são tensões superiores — por isso `(5-)` vira
meio-diminuto, não tom fantasma.

## Faseamento (Opção 2, começando pela 1)

1. **Fase 1 — `Chord` delega.** Reescrever os internos de
   `harmonic_analysis.domain.chord.Chord` para derivar `quality`/`is_minor`/
   `is_dominant_seventh`/`properties` do mesmo motor de intervalos que `realize()`
   usa. API pública estável → ~34 testes seguram o comportamento; o bug do
   dominante e o dialeto `±` morrem numa fonte só.
2. **Fase 2 — extrair `ParsedChord`.** Promover o parse estruturado para
   `cifra_core.theory`; `realize()` e `Chord` passam a derivar dele. O scraper
   poderia validar acordes pela mesma porta.

## Non-goals

- *Voicing*, dobramentos, supressões, registro (a cifra não os estabelece).
- Classificação acorde-vs-letra / falso-positivo `N.C.→C` (portão de extração;
  fio separado, a montante).
- OMR / leitura de pauta do PDF.
- Reproduzir texto, tabelas-como-diagramadas ou as 70 análises do livro.
