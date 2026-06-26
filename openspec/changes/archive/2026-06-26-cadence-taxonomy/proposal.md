## Why

A análise de cadências (`analyze_cadences`) é mais pobre que a taxonomia da
fonte (Chediak Vol. I, XXXII, pp. 109-111), que define **cinco** cadências:

- **perfeita** = V→I em estado fundamental (a mais forte, conclusiva);
- **imperfeita** = V→I com inversão, **ou** VII→I (enfraquece) — *não temos*;
- **plagal** = IV→I **ou IIm→I** — só temos IV→I;
- **meia-cadência** = qualquer grau → V;
- **deceptiva** = V → qualquer grau que **não** seja a tônica — só temos V→vi.

Hoje há 4 categorias (Autêntica/Plagal/Interrompida/Meia-cadência) com definições
estreitas: a deceptiva só pega V→vi, a plagal ignora o IIm→I, e não há distinção
perfeita/imperfeita (a contribuição central do Chediak nesse capítulo).

## What Changes

- **Nova capability `harmonic-cadence`** com as 5 cadências do Chediak + a
  **autêntica** (perfeita precedida de subdominante, IV/II→V→I).
- Distinguir **perfeita vs imperfeita** pela inversão do baixo (slash) e pelo
  VII→I; **deceptiva** = V→não-tônica; **plagal** inclui IIm→I.
- Atualizar os consumidores: `explain/prompt` (lê Perfeita+Autêntica) e o teste
  de cadência.

Fora de escopo: deceptiva **modulante** (V que leva a nova tonalidade) — depende
da detecção de modulação (`key-detection`/`segment_keys`), fica como follow-up.

## Capabilities

### New Capabilities
- `harmonic-cadence`: taxonomia das cinco cadências (perfeita, imperfeita,
  plagal, meia-cadência, deceptiva) + a autêntica, conforme Chediak.

## Impact

- `harmonic_analysis/domain/cadence.py`: reescrito sobre `degree_base` e detecção
  de inversão (baixo).
- `harmonic_analysis/explain/prompt.py`: lê `Perfeita`/`Autêntica`.
- Testes: `test_harmony` (chave `Perfeita`); novos cenários de cadência.
