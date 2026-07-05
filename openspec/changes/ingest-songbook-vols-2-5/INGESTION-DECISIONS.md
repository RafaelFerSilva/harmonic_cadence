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

## Falta (próximas sessões)
Vol. 5 (65 músicas, índice próprio, task #2) · docs AGENTS.md/ROADMAP.md (task 5.1-5.2:
Vol.1 = corpus n=62; números novos) · buscar `se-e-tarde-me-perdoa` no Vol. 5.
