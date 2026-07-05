# Decisões de ingestão — ingest-songbook-vols-2-5

Registro honesto de colisões, correções de fato e pendências encontradas na
varredura (tarefa 5.3). Fonte: `songbooks/Songbook - bossa Nova Vol 2.pdf`
(offset PDF = livro − 25, confirmado: PDF 5 = livro 30 "Águas de março").

## Reconciliação de bookkeeping (2026-07-05)

Uma sessão anterior transcreveu **47 arquivos do Vol. 2** (todos passando o gate
de admissão) mas **não marcou** `tasks.md` nem as worklists. Estado real vs.
documentado divergia. As worklists foram **re-sincronizadas** com o disco
(`cifras/<slug>.md` existe ⇒ `[x]`). Nenhuma sobrescrita: colisão de slug nunca
ocorreu (todos os writes foram de arquivos novos).

## Correções de fato (o header do livro é a autoridade — D5)

- **`bloco-do-eu-sozinho`**: a worklist provisória (índice-irmão do Vol. 1) supunha
  compositores "Marcos Valle e Paulo Sérgio Valle". O **cabeçalho da página do livro
  (p.43) imprime "MARCOS VALLE E RUY GUERRA"** — usado no arquivo. (Curiosidade: a
  página de copyright, p.45, credita "Marcos Valle e Paulo Sérgio Valle" — divergência
  do próprio livro; o cabeçalho da música prevalece por protocolo.)

## Ordem do livro NÃO é alfabética (fato operacional)

Confirmado na varredura: livro 33 = Ana Luiza, 36 = Amei tanto (invertidos);
51 = Desejo do mar (D) **antes** de 52 Canção do amanhecer e 54 Canção que morre no
ar (C). A **varredura sequencial do miolo é a única verdade** (worklist = só
checklist de cobertura, como o cabeçalho dela já avisa). Não há atalho alfabético.

## Fantasmas do índice-irmão (varredura COMPLETA do Vol.2, livro pp.26–143)

O índice-irmão (Vol. 1) lista **duas entradas que NÃO existem no Vol. 2** — a varredura
sequencial página-a-página do miolo inteiro (a autoridade, D1) as descartou:
- **"Eu sei que…"** (entrada ilegível/incerta no índice-irmão): nenhuma música com esse
  título em todo o volume. Leitura espúria do índice.
- **`se-e-tarde-me-perdoa`**: NÃO aparece no Vol. 2 (varri toda a seção "S": Sabe você,
  Samba da benção, Samba da pergunta, Samba do carioca, Sem mais adeus, Só danço samba,
  Só por amor, Sonho de lugar — e todo o resto até Zelão, a última música, livro p.142).
  Provável: está em OUTRO volume (o índice-irmão do Vol.1 pode listar títulos de vários
  volumes) ou o índice tinha erro. Marcada `[!]` na worklist. **Candidata a buscar no
  Vol. 5** (ou reconciliar quando os demais volumes forem varridos).

Efeito: o Vol. 2 tem **60 músicas reais** (não 61/62) — os 2 fantasmas saem do denominador.

## Transcritas e verificadas nesta sessão (14 — todas `ok`)

Varredura sequencial completa do PDF (livro pp.26–143), só-acordes (anti-filtro),
normalização de empilhado (`X⁶₉`→`X6(9)`, `X⁷₄`→`X74`), manifesto dos diagramas da cifra:
`ausencia-de-voce` (p.40) · `berimbau` (p.46) · `bloco-do-eu-sozinho` (p.43) ·
`bye-bye-brasil` (p.48) · `cancao-do-amanhecer` (p.52) · `cancao-que-morre-no-ar` (p.54)
· `desejo-do-mar` (p.51) · `ilusao-a-toa` (p.78) · `manha-de-carnaval` (p.84) ·
`samba-da-pergunta` (p.116) · `trocando-em-miudos` (p.136) · `ultimo-canto` (p.138) ·
`vagamente` (p.140) · `zelao` (p.142).

Ajustes forçados pelo gate de admissão (nenhuma fabricação):
- `ausencia-de-voce`: diagrama lido como `Eb7M(6)` era `Eb7M`.
- `ilusao-a-toa`: `Abm7` é diagrama SÓ da partitura (não da cifra) → excluído do manifesto
  (acordes de pauta nunca entram, D2).
- `manha-de-carnaval`: o cliché descendente de abertura (i → i7M → i7 → i6) é diagramado
  com alterações empilhadas ilegíveis nesta resolução; colapsado ao `Am(add9)` base
  (definitivamente correto, **funcionalmente invariante** = tônica `i`; nunca palpite).

## Fechamento do Vol. 2

**60/60 músicas reais ingeridas** (46 de sessão anterior + 14 desta). Corpus 217 → **231**.
Baseline funcional no denominador novo (pausa-e-investiga): **gates duros 231/231 verdes**
(diminuto, D2, cadência×função) — a teoria generaliza sem defeito. Centro: cobertura
207/231, concordam 170/207 (82%). Ledger de trítono: 32 em 16/231 (worklist de adjudicação,
não defeito). **496 testes verdes** (sem mudança de motor). `audit_completeness`: novas entram
`complete` (verificação extração⊇diagramas na admissão).

## Vol. 5 — EM ANDAMENTO (offset PDF=livro−25, confirmado PDF 6 = livro 31)

O Vol. 5 tem **índice próprio com páginas do livro** (PDF pp.3-4) — mais fácil de navegar
que o Vol. 2, mas o miolo ainda decide (índice é alfabético; miolo segue as páginas, com
músicas fora de ordem alfabética: Bolinha de papel/B em p.31 abre o volume).

Transcritas e verificadas (11 — todas `ok`, livro pp.31–50): `bolinha-de-papel` (p.31) ·
`amor-certinho` (p.32) · `amor-em-paz` (p.34) · `a-mulher-de-cada-porto` (p.36) ·
`aos-pes-da-cruz` (p.38) · `aqui-o` (p.40) · `cai-a-tarde` (p.43) · `baiaozinho` (p.44) ·
`beatriz` (p.46) · `bons-amigos` (p.48) · `caminho-de-pedra` (p.50).

Correções de fato / decisões (Vol. 5):
- **`aos-pes-da-cruz`**: título impresso é "Aos pés da cruz" (a worklist supôs "santa cruz" —
  é a LETRA que canta "aos pés da santa cruz"). Slug corrigido; compositor pelo header
  (Zé Gonçalves e Marino Pinto).
- **`omit3` não é representável no parser** (achado por probe: `extract_chords_from_lines`
  devolve `[]` para `F#7(9 omit3)` — o espaço + `omit3` quebra o token). Como é detalhe de
  voicing (dominante sem 3ª) e o motor é **funcional**, mapeado para a forma sem-omit
  (`F#7(9 omit3)`→`F#7(9)`; idem `G7`, `B7(b9)`): pitch-fiel no que soa (raiz/5/b7/9),
  função idêntica (dominante). Afeta `aqui-o`, `caminho-de-pedra`. Nunca fabricação.
- Alterações múltiplas usam a forma de **barra** que o parser aceita: `A7(9/#11/13)`,
  `C#7(b9/#11)`, `E6(9/#11)`, `Bb7(b9/#11)` etc. (a forma de parênteses duplos `E6(9)(#11)`
  é evitada). Toninho Horta (`aqui-o`, `bons-amigos`) e Edu Lobo (`beatriz`) passam `ok`.
## Fechamento do Vol. 5 (2026-07-05) — varredura sequencial completa (livro pp.31–160)

A varredura do miolo inteiro (PDF 4–134; pp.135–137 = apêndice de entrevistas, sem
músicas) fechou o volume. O **índice próprio do Vol. 5 (PDF p.3)** declara **63 músicas** e
foi decisivo para resolver as 3 pendências da worklist (que tinha 65 entradas):

- **`isaura`** (Herivelto Martins e Roberto Roberti, livro p.90): **REAL** (consta no índice,
  entre Fotografia/89 e Janelas abertas/92), mas é um **GAP DE DIGITALIZAÇÃO** — o PDF pula de
  Fotografia (livro 89 = PDF 64) direto para Janelas abertas (livro 92 = PDF 65); as **páginas
  90–91 (Isaura) faltam no scan**. Prova: o offset PDF↔livro salta de −25 para −27, exatamente
  as 2 páginas ausentes. Irrecuperável sem nova varredura da fonte. Marcada `[!]`, honesta.
- **`bate-boca`** e **`bonita`** (ambos "Tom Jobim"): **FANTASMAS** — NÃO constam no índice do
  Vol. 5 (as entradas em "B" são só Baiãozinho, Beatriz, Bolinha de papel, Bons amigos). Mesmo
  caso dos 2 fantasmas do Vol. 2: a worklist herdou títulos de índice-irmão. Marcados `[!]`.

Contabilidade que fecha: **63 reais = 62 transcritas+verificadas + 1 (Isaura) gap de scan**;
`bate-boca`/`bonita` nunca existiram no volume (saem do denominador). A capa confirma "63 músicas".

Achados de parser na 2ª metade (nenhuma fabricação): `add9` é aceito (`Cm(add9)`, `Ab(add9)`,
`F(add9)/A`); `Cm(b6)`, `6(9)` com baixo (`Bb6(9)/F`, `E6(9)/B`), enarmônicos (`Cb6(9)/Gb`),
diminutos com baixo (`D°/Eb`, `B°/C`, `C#°/D`) e min-maj com 9 (`Cm(7M/9)`, `Em(7M/9)`) todos
parseiam. `A7(9 omit3)`/`A7(b9 omit3)` (Samba do avião) mapeados p/ `A7(9)`/`A7(b9)` (mesma regra
do `omit3`). `rosa-morena`: o gate pegou um `D#°` de passagem omitido no corpo (estava no diagrama
+ partitura, D7M→D#°→G#7(b9)) — corrigido. Composições de `F` nu (Menino das laranjas) e `G7M`
(Praia branca) que só a partitura confirma entraram no header como whitelist do extrator.

## Fechamento da change

Corpus **231 → 293** cifras reais (`.md`). Baseline funcional no denominador novo (pausa-e-
investiga): **3 gates duros 293/293 verdes** (diminuto XXI-XXII, D2 XIX, cadência×função XXXII)
— a teoria generaliza no dado ampliado sem defeito. Centro: cobertura 262/293, concordam
216/262 (82%). Ledger de trítono: 43 em 20/293 (worklist de adjudicação, não defeito).
`audit_completeness` (n=293): **SEM drift**. `se-e-tarde-me-perdoa` (fantasma do Vol. 2)
**não está no Vol. 5** — permanece fantasma sem volume de origem identificado.

## Falta (próximas sessões)
`corpus build`/`gates`/`report` DuckDB final (tarefa 4.2, adiada) · arquivar a change ·
(oportunístico) re-scan da fonte p/ recuperar Isaura; auditoria ampla Vol.1/Vol.4×livro.
