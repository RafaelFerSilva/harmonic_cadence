## Why

A migração para o modelo de nota soletrado (`cifra_core.theory.Note`) ficou pela
metade. Em `domain/harmony.py` a escala já é construída soletrada (Fá maior com
`Bb`), mas a **descrição de empréstimo modal** ainda passa pelo caminho legado
sustenido-só (`_transpose_scale`/`normalize_note` sobre `CHROMATIC_NOTES`) e
mostra `A#` onde o Chediak grafa `Bb` — num campo **visível ao usuário** ("Origem
do Empréstimo", presente nos relatórios MD/JSON/HTML).

Isto **viola uma regra que já está nas specs**: `music-theory-core` exige que a
análise "MUST NOT collapse flats into sharps". Da mesma forma, `key-detection` já
determina que a detecção K-S "SHALL replace the first-chord/minor-ratio heuristic"
— mas a heurística `guess_key` sobrevive como fallback em dois entry points. Esta
change **fecha o gap entre spec e código** e aposenta o subsistema sharp-only de
uma vez (em vez de deixá-lo apodrecer), agora que o terreno está limpo.

## What Changes

Quatro frentes que tocam o **mesmo** subsistema legado (por isso uma change só):

- **Spelling correto (corrige bug visível):** rotear `describe_modal_borrowing` e
  `_build_harmonic_field` por `Note` + `build_scale` (soletrado), com um mapa das
  chaves PT legadas (`"menor_harmonica"`, …) para os nomes de modo do `build_scale`
  (`harmonic_minor`, …). Saída passa a grafar `Bb`, `Eb`, `Ab` corretamente.
- **Campo modal derivado (fonte única):** aposentar `constants.MODE_HARMONY` e
  `constants.MODES` — o campo (grau, qualidade) passa a ser derivado de
  `build_scale`/`_tetrad_quality`, correto por construção (casa Chediak pp. 122-125).
- **Matemática de intervalo soletrada:** rotear `_get_interval`/`normalize_note`
  por `Note.pitch_class` (`interval_semitones`); aposentar `constants.NOTE_REPLACEMENTS`
  e o `normalize_note` sustenido-só. (Os intervalos já eram corretos — invariantes
  por enarmonia —, isto é consolidação.)
- **Detecção de tom unificada:** trocar `guess_key`→`detect_key` nos entry points
  standalone `build_functional_parse(symbols)` e `reharmonize_symbols(symbols)`;
  aposentar `HarmonicAnalysis.guess_key`.

Antes de remover qualquer legado, **adicionar testes de caracterização** (não
existe rede que fixe o spelling de saída hoje).

## Capabilities

### New Capabilities

Nenhuma. Toda a funcionalidade já existe; esta change a torna conforme às specs.

### Modified Capabilities

- `modal-tonal-center`: estende a garantia de fonte única (adicionada em
  `remove-dead-code`) para exigir que a **descrição de empréstimo modal e o campo
  modal derivado preservem a grafia enarmônica** (`Bb`, não `A#`), via o modelo
  `Note` soletrado. Corrige comportamento observável.
- `key-detection`: adiciona cenário tornando a regra existente ("replace the
  first-chord/minor-ratio heuristic") válida em **todos** os entry points — o
  parsing funcional e a reharmonização standalone passam a usar `detect_key`, não
  a heurística. Sem a heurística sobrevivente.

### (verificar na implementação)
- `harmonic-function`: a descrição da função `Emp` é produzida por
  `describe_modal_borrowing`; se um cenário precisar fixar a grafia ali, adicionar
  como ADDED. Caso contrário, o delta de `modal-tonal-center` cobre.

## Impact

- **Código:** `domain/harmony.py` (borrowing, campo, intervalos), `domain/constants.py`
  (remove `MODE_HARMONY`, `MODES`, `NOTE_REPLACEMENTS`), `domain/functional_hmm.py`
  e `domain/reharmonization.py` (fallback de tom). Possível helper de mapa PT→EN.
- **Saída:** o campo "Origem do Empréstimo" passa a grafar bemóis corretamente —
  **mudança observável e desejada** nos relatórios MD/JSON/HTML.
- **Testes:** + caracterização (Bb-não-A#, campo == Chediak, tom unificado);
  suíte completa (248) verde, ruff limpo ao fim.
- **Risco:** médio. O `describe_modal_borrowing` lista *todos* os modos paralelos
  de onde um acorde poderia vir — esse comportamento (multi-origem) deve ser
  preservado, só com grafia correta. Mitigado por testes-primeiro.
