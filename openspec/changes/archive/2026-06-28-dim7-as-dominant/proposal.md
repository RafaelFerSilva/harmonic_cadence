## Why

Um acorde diminuto com sétima (`dim7`/`°7`, ex.: `B°7` = B-D-F-Ab) **é** um dominante
com nona menor sem fundamental (V7(b9) *rootless*): `G7(b9)` = G-B-D-F-Ab; tire o G e
sobra exatamente `B°7`. Logo `B°7` é o dominante de C (resolve meio-tom acima da sua
fundamental escrita). Hoje o analisador trata todo `dim7` como um acorde de categoria
`DIMINISHED` inerte na camada funcional: ele **não** entra na detecção de dominante
aplicado, **não** recebe escala-acorde, e sua origem dominante fica invisível — perdendo
a leitura funcional mais comum do diminuto na MPB/choro (o diminuto ascendente
`I #I°7 ii` é onipresente). Esta é a change própria que o ROADMAP adiou de propósito
("dim7-como-dominante (viio7 = V7b9)").

A simetria do `dim7` (terças menores empilhadas) o torna ambíguo — `B°7` = `D°7` = `F°7`
= `Ab°7` enarmonicamente, e cada um pode ser o V7(b9) de quatro tônicas. A resolução real
é decidida pelo **contexto** (o acorde seguinte), exatamente o tipo de juízo funcional que
o projeto já faz para `V7`/`SubV`.

## What Changes

- Reconhecer um `dim7` como **V7(b9) sem fundamental**: a fundamental do dominante
  implícito é uma 3ª maior abaixo da fundamental escrita; a tônica de resolução é um
  semitom acima. Quando o `dim7` resolve no acorde um semitom acima de sua fundamental,
  classificá-lo como **dominante** — primário (`V7(b9)` de I) ou **secundário rootless**
  (`V7(b9)/x`), análogo ao `V7/x` já detectado.
- Distinguir o **dim7-dominante** (resolve um semitom acima) do **dim7 de aproximação /
  passagem** (bordadura cromática sem resolução dominante), que NÃO recebe função
  dominante — evitando rotular todo diminuto como dominante.
- Dar ao `dim7`-dominante a **escala-acorde diminuta** (octatônica, igual ao `G7(b9)` que
  o código já mapeia), em vez de nenhuma escala.
- Atribuir **função dominante (D)** ao `dim7`-dominante na análise funcional, inclusive
  quando cromático (não-diatônico).
- **Preservar** a notação visual: o numeral romano continua exibindo `vii°7` / `#i°7`
  (a marca `°` é a identidade sonora, Chediak pp. 77/85); a leitura dominante entra como
  **glosa funcional** (ex.: "`#i°7` = V7(b9)/ii"), não como troca do numeral.

## Capabilities

### New Capabilities
<!-- Nenhuma capability nova: é extensão coesa de capabilities existentes. -->

### Modified Capabilities
- `applied-dominant-analysis`: estende a detecção de dominante para incluir o `dim7` como
  `V7(b9)` rootless (primário/secundário) pela resolução um semitom acima, e distingue o
  diminuto de aproximação (sem função dominante).
- `harmonic-function`: um `dim7` que resolve como dominante carrega função **D** mesmo
  quando cromático; o diminuto de aproximação não.
- `chord-scale-tensions`: o `dim7`-dominante mapeia para a escala diminuta (octatônica),
  consistente com o mapeamento `b9 → diminished` já existente.

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/harmony.py` (análise de
  função / dominante aplicado), `harmonic_function.py`, `chord_scale.py` (escala do
  dim7-dominante), `roman.py`/relatório (glosa funcional, preservando `°7`). Testes novos
  em `test_applied_dominants.py`, `test_harmonic_function.py`,
  `test_altered_dominant_scales.py`/`test_chord_scale.py`.
- **NÃO tocado (decisão de risco):** o parsing e o enum `Category` (um `dim7` continua
  `Category.DIMINISHED` por som — a tese é sobre **função/origem**, não identidade); e o
  `_tritone_gate`/`detect_key` (a detecção de tonalidade fica **idêntica** — a relação
  dim7↔detecção de tom fica para uma change futura, medida). Isso garante **zero
  regressão** das 4 métricas Cifra-Club e do centro tonal.
- **Trava inegociável:** rodar `scripts/key_baseline.py` ao vivo e a suíte completa antes
  de arquivar; zero regressão das corretas (a regra que já barrou 2 ships).
- **A confirmar contra Chediak:** a página exata do enunciado "diminuto = V7(b9) sem
  fundamental" (a derivação pelas notas é fato; a citação será fixada no apply, lendo
  `base_estudo/` — nunca chutar o número).
