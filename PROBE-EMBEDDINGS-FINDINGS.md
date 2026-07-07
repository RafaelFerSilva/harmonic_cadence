# Probe Fase 0 — embeddings aprendidos vs. Fingerprint à mão (2026-07-07)

> Experimento go/no-go do plano `ML-EVOLUTION-PLAN.md`. **Veredito: NO-GO para
> embeddings de acorde aprendidos ingênuos** — quebram a invariância de transposição
> (o princípio central do projeto) e não superam o baseline à mão. Precedente de método:
> `PROBE-FINDINGS.md` (probes exploratórios são documentados, não viram spec permanente).

## Pergunta

Embeddings de acorde/música **aprendidos** (chord2vec skip-gram) batem o `Fingerprint`
à mão (`domain/style_fingerprint`, features de FUNÇÃO) nas tarefas descritivas (similaridade/
clustering), **preservando a invariância de transposição** que é lei do projeto?

## Método (runnable, in-corpus, sem download externo)

- Dados: sequências de acorde por música do `corpus.duckdb` (293 músicas, 15.343 ocorrências).
- Modelos: `gensim` Word2Vec (skip-gram, dim=64, window=4, epochs=40), duas variantes:
  **RAW** (293 sequências) e **AUG** (293×12 transposições — augmentation por tom).
- Embedding de música = média dos vetores de acorde (mean-pooling).
- Transpositor de símbolo próprio (raiz + baixo `/X`, grafia canônica) — sem dep no motor.

## Resultados

| Representação | (1) Invariância de transposição¹ | (2) Vizinhos (qualitativo) |
|---|---|---|
| **Fingerprint à mão** | **~1.000** (por construção) | plausíveis, validados (docs) |
| chord2vec RAW | **0.678** | plausíveis, sem vantagem clara |
| chord2vec AUG (12 transp.) | **0.629** | plausíveis, sem vantagem clara |

¹ média do cosseno entre o embedding de uma música e o da MESMA música transposta (k=1..11).
Uma representação transposição-invariante = 1.0. Vocab: RAW=670, AUG=1800.

Vizinhos aprendidos (AUG) — plausíveis mas nada obviamente melhor que o à mão:
`garota-de-ipanema → baiaozinho / pernas / ainda-mais-lindo / samba-de-verao`;
`inutil-paisagem → praias-desertas / chega-de-saudade / cansei-de-ilusoes`.

## Leitura (o achado)

1. **O embedding aprendido quebra a invariância de transposição (0.63–0.68 vs. 1.0).** É uma
   violação direta do princípio central: a identidade harmônica de uma música NÃO deve depender
   do tom (a análise funcional é invariante a transposição). O chord2vec cru faz a identidade
   depender do tom — regressão conceitual, não progresso.
2. **Augmentation NÃO resgata** (0.629 < 0.678): treinar nas 12 transposições espalha o vocab
   (670→1800) e o mean-pooling de grafias enarmônicas distintas não produz alinhamento. A
   invariância teria de ser **arquitetural** (espaço de função/intervalo), não aprendida por força.
3. **Sem vantagem descritiva** que compense: os vizinhos são plausíveis mas não melhores que o
   Fingerprint (que já dá vizinhos validados: garota → o-amor-que-acabou/alvorada, docs).

**O Fingerprint à mão é SUPERIOR aqui — não por acaso, mas porque codifica o inductive bias
certo (invariância de transposição via features de FUNÇÃO) por construção.** Aprender do zero
joga isso fora.

## Consequência para o `ML-EVOLUTION-PLAN`

- **A Frente A (embeddings ingênuos de acorde) é NO-GO** como estava desenhada.
- O achado é **mais forte que o problema de dado**: transferência externa (Frente B) daria mais
  dado, mas a MESMA arquitetura (espaço de acorde absoluto) ainda quebra a invariância. Logo o
  download externo **não era o gargalo** — o gargalo é arquitetural.
- Para DL valer aqui, uma representação aprendida teria de ser **transposição-invariante por
  design** (operar em espaço de FUNÇÃO/INTERVALO) — mas isso é justamente re-derivar o inductive
  bias do Fingerprint, agora aprendido, para ganho marginal incerto. Barra alta, ganho duvidoso.
- **A stack de DL NÃO se paga por esta via.** Onde DL ainda pode ter valor (não testado, não
  urgente): (a) modelo de sequência NEURAL de FUNÇÃO (14 símbolos, já invariante) para surpresa —
  mas o n-grama Witten-Bell já é quase-ótimo nesse vocab denso; (b) Frente C (classificador nos
  rótulos), gated por MAIS LABELS (adjudicação humana), não por mecanismo.

## Recomendação

**Não** produtizar embeddings aprendidos. Manter o `Fingerprint` à mão (vence no princípio e no
resultado). O maior retorno de esforço continua sendo **fechar a adjudicação humana dos ~83
vereditos ambíguos** (cresce labels, melhora tudo, custo-zero de aquisição) — não DL, não dado novo.

Deps de ML (`numpy`/`gensim`/`scipy`) instaladas só no venv para o probe; **não** entram no
`pyproject` (o núcleo segue stdlib-puro; o probe não justificou o peso).
