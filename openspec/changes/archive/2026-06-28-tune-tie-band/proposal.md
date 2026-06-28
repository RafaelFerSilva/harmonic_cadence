## Why

`detect_key` retorna "A minor" para "Papel Marché" (João Bosco) quando o gold do Cifra Club é "C major". A causa é dupla: linhas de afinação da cifra ("Afinação Drop D: D A D G B E") são parseadas como acordes e poluem o perfil K-S, e o `TIE_BAND=0.06` é pequeno demais para deixar C major entrar na banda de desempate — apesar de a corroboração cadencial já apontar C major com força (corrob=7.00 vs 0.00 de A minor). A correção é cirúrgica e não altera a lógica das Fases B v1/v2.

## What Changes

- `cifra_core/lines.py`: adicionar `_AFIN_RE` para filtrar linhas de afinação ("Afinação", "Drop", "Capotraste") antes que o extrator de acordes as processe.
- `harmonic_analysis/domain/key_detection.py`: aumentar `TIE_BAND` de `0.06` para `0.10`, permitindo que candidatos com gap até 10% entrem na banda de desempate cadencial.
- `scripts/key_baseline.py`: rodar e documentar o novo baseline (n=60) confirmando que Papel Marché passa a C major sem regressões.

## Capabilities

### New Capabilities

*(nenhuma — mudança puramente de calibração e filtro de ruído)*

### Modified Capabilities

- `cifra-core`: o filtro canônico de linhas (`clean_cifra_lines`) passa a descartar linhas de afinação de instrumento, ampliando o escopo de "ruído" reconhecido.
- `key-detection`: o parâmetro `TIE_BAND` é recalibrado de 0.06 para 0.10; a banda de desempate cadencial fica mais abrangente sem alterar a lógica de corroboração ou o gate de âncora-baixo da v2.
- `key-accuracy-evaluation`: o baseline esperado muda — Papel Marché passa de "ERRO" para "exato"; documentar novos números (modo/tônica/relativa).

## Impact

- `packages/cifra_core/src/cifra_core/lines.py` — adição de uma regex e um branch em `_is_noise`.
- `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py` — alteração de uma constante (`TIE_BAND`).
- `scripts/key_baseline.py` — execução e documentação (sem alteração de código).
- Testes: `test_key_corpus.py` (sintético, deve continuar 100%), `test_tonal_center_detection.py` e `test_parallel_mode_correction.py` (regressão — nenhum comportamento esperado muda), e um novo caso de teste cobrindo a filtragem da linha de afinação em `cifra_core/tests/`.
