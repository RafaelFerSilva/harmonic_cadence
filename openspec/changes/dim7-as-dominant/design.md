## Context

O parser já modela o `dim7` corretamente como som: `B°7` → `Third.MINOR + Fifth.DIMINISHED
+ Seventh.DIMINISHED` → `Category.DIMINISHED`, com a 7ª diminuta implícita (Chediak pp.
77/85: `°` inclui a 7ª). O que falta é a **leitura funcional**: hoje `harmony.analyze_function`
só entra no caminho de dominante quando `chord.is_dominant_seventh` (verdadeiro apenas para
`Category.DOMINANT`), então todo `dim7` escapa da detecção de dominante aplicado
(`harmony.py:113`), não recebe escala-acorde (`chord_scale.recommended_scale` retorna `None`,
`chord_scale.py:75`) e tem só a função diatônica por grau (`vii°7 → D`,
`harmonic_function.py:16`). A origem dominante — a leitura mais comum do diminuto na MPB e no
choro — fica invisível.

A tese é aritmética e incontestável: `V7(b9)` = fundamental + 3ªM + 5ªJ + 7ªm + 9ªm; as
quatro notas acima da fundamental formam um `dim7`. Logo `dim7` = `V7(b9)` sem fundamental,
e a fundamental implícita está uma 3ªM abaixo da fundamental escrita (a tônica de resolução,
um semitom acima). A simetria do `dim7` (terças menores) o deixa ambíguo entre quatro
dominantes; o **contexto** (o acorde seguinte) desambigua — o mesmo juízo que o projeto já
faz para `V7/x` e `SubV`.

Restrição inegociável do projeto ([[tritone-gate-quality-lesson]]): toda recalibração mede
contra `scripts/key_baseline.py` ao vivo, zero regressão das corretas; seções degradam
visíveis. Regra de ouro recém-codificada: o significado é produzido pelo motor + Chediak,
não lido da fonte.

## Goals / Non-Goals

**Goals:**
- Ler um `dim7` que resolve um semitom acima como `V7(b9)` rootless — primário (`V7(b9)` de
  I) ou secundário (`V7(b9)/x`) — atribuindo função dominante e escala diminuta.
- Distinguir o dim7-dominante do dim7 de aproximação/passagem (sem função dominante).
- Preservar a notação `°7` no numeral; a leitura dominante é glosa funcional.

**Non-Goals:**
- **Não** mudar o enum `Category` nem o parsing — um `dim7` continua `DIMINISHED` por som; a
  tese é sobre função/origem, não identidade.
- **Não** tocar `_tritone_gate`/`detect_key` — a detecção de tonalidade fica byte-idêntica
  (a relação dim7↔detecção de tom é uma change futura, medida). Isso garante zero regressão
  das 4 métricas Cifra-Club + centro tonal.
- **Não** mexer em `chord.is_dominant_seventh` (vaza para todo o pipeline) — usar um caminho
  dim7-específico.
- **Não** tratar (nesta v1) o diminuto de resolução descendente (ex.: `Ab°7→G`) nem exigir
  que o alvo seja estável — ficam para refinamento guiado por corpus.

## Decisions

### D1 — Atuar na camada de função, com caminho dim7-específico (não em `is_dominant_seventh`)

Adicionar a lógica em `harmony.analyze_function` num ramo próprio para `Category.DIMINISHED`
com 7ª, espelhando o ramo de dominante secundário, **sem** alterar `chord.is_dominant_seventh`
nem `Category`. *Por quê:* mudar `is_dominant_seventh` para incluir diminutos vazaria para
`chord_scale`, RNA e qualquer consumidor do predicado, ampliando o raio de risco; um ramo
dedicado mantém a mudança cirúrgica e auditável.

### D2 — Critério de resolução: alvo um semitom acima da fundamental escrita

Classificar como dominante sse o próximo acorde tem fundamental (ou baixo) = `raiz_dim7 + 1`.
A fundamental do dominante implícito = `raiz_dim7 − 4`; o alvo é primário se for a tônica do
tom, secundário se for outro grau diatônico/tonicizado (rotular `V7(b9)/x` pelo grau do
alvo). *Por quê esse critério e não "qualquer das 4 resoluções":* a resolução ascendente por
semitom é a canônica e a única não-ambígua a partir do **spelling escrito**; aceitar as
quatro tornaria quase todo encadeamento "dominante" e geraria falsos. Conservador primeiro;
medir e afrouxar depois se o corpus pedir.

### D3 — Dim7 de aproximação/passagem fica sem função dominante

Se não há resolução por semitom ascendente, o diminuto é de aproximação/passagem (bordadura,
cromático) e **não** recebe função dominante nem escala dominante — reportado como diminuto
de aproximação. *Por quê:* a simetria do `dim7` exige um gate explícito para não inflar
dominantes; espelha o requisito existente "Dominant-quality chords without dominant function".

### D4 — Escala diminuta para o dim7-dominante

Mapear o dim7-dominante para a escala diminuta (octatônica) que contém suas notas — igual ao
`G7(b9) → diminished` que `_altered_dominant_scale` já produz (`chord_scale.py:47`). Reusar
`build_scale(root, "diminished")`. *Por quê:* consistência com o tratamento de `b9` já
especshado em chord-scale-tensions; a octatônica do dim7 é a mesma do V7(b9) implícito.

### D5 — Numeral preserva `°7`; a glosa carrega a função

`roman.py` continua emitindo `vii°7`/`#i°7` (a marca `°` é identidade sonora, Chediak p.85).
A leitura dominante aparece como glosa funcional no relatório (ex.: "`#i°7` = V7(b9)/ii"),
não como troca do numeral. *Por quê:* preserva a legibilidade e a verdade sonora; a função é
uma camada interpretativa por cima, não uma reescrita.

## Risks / Trade-offs

- **[Mudar `is_dominant_seventh`/`Category` regrediria o pipeline inteiro]** → ramo
  dim7-específico; `Category` e o predicado ficam intactos; cobertura por teste de que
  `B°7` continua `Category.DIMINISHED`.
- **[Enarmonia: o spelling escrito decide a resolução; cifra mal-grafada falha]** → usar a
  fundamental escrita (o Cifra Club costuma grafar o diminuto pela função, ex.: `C#°7` antes
  de `Dm`); registrar como limitação conhecida; o caso descendente fica fora da v1.
- **[Falso-positivo: alvo um semitom acima por acaso (passagem ascendente)]** → o critério já
  é específico; medir no corpus e, se necessário, exigir alvo de repouso numa v2.
- **[Regressão na detecção de tom]** → impossível por construção: `detect_key`/`_tritone_gate`
  não são tocados. A trava (`key_baseline.py` ao vivo) confirma 4 métricas + centro idênticos.

## Migration Plan

1. Implementar o ramo dim7-dominante em `harmony.py` + função/escala, com testes unitários
   (B°7→C, C#°7→Dm, F#°7→G; passagem → sem dominante).
2. Glosa funcional no relatório, preservando `°7`.
3. Rodar a suíte completa (`make test`) e `scripts/key_baseline.py` ao vivo; confirmar 4
   métricas Cifra-Club + centro tonal **idênticos** ao baseline atual (modo 86 · exata 69 ·
   relativa 76 · coleção 97 · centro 79).
4. Fixar a citação de página de Chediak (ler `base_estudo/`) antes de gravar o texto PT-BR.
   Rollback = remover o ramo dim7; nada mais foi tocado.

## Open Questions

- **Citação de Chediak:** a página exata do enunciado "diminuto = V7(b9) sem fundamental"
  (a derivação pelas notas é fato; a página será confirmada no apply — nunca chutar).
- **Resolução descendente / alvo estável:** incluir `Ab°7→G` e exigir alvo de repouso são
  refinamentos de v2, decididos por medição no corpus.
- **Glosa no relatório:** formato exato do texto PT-BR ("dominante rootless de…", "V7(b9)/ii")
  — resolver na implementação do relatório.
