## Why

O `modal-harmonic-field` destilou o campo diatônico de cada modo, mas deixou de
fora a **seleção cadencial** de Chediak (pp. 122-125): quais acordes do modo
firmam o "sabor" modal numa cadência, e quais **evitar** (porque puxam de volta
ao tonalismo maior/menor). Essa seleção é *curatorial* (não derivável do campo) —
é conhecimento da fonte que vale capturar.

Exemplos: no **dórico**, os cadenciais são `IIm7`/`IV7`/`bVII7M` e evita-se o
`VIm7(b5)`; no **mixolídio**, `I7`/`Vm7`/`bVII7M`, evita-se o `IIIm7(b5)`.

## What Changes

- **`MODAL_CADENTIAL`** e **`MODAL_AVOID`** por modo (tétrades, Chediak pp. 122-125).
- Surfacing na seção `modal_analysis` do relatório: `cadential_chords`,
  `avoid_chords` e a `characteristic_note` (que já existia, mas não era exposta).

Fora de escopo: as tríades cadenciais (mantemos as tétrades, mais usadas em
harmonia); lócrio e iônico não têm seleção cadencial própria no livro.

## Capabilities

### Modified Capabilities
- `modal-tonal-center`: expõe os acordes cadenciais e evitados característicos de
  cada modo, além da nota característica.

## Impact

- `harmonic_analysis/domain/modal.py`: `MODAL_CADENTIAL`, `MODAL_AVOID`.
- `harmonic_analysis/services/analysis_service.py`: a seção `modal_analysis`
  ganha `characteristic_note`, `cadential_chords`, `avoid_chords`.
- Testes: as tabelas conferem com Chediak por modo.
