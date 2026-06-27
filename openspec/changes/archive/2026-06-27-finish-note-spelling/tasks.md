## 1. Rede de caracterização (test-first)

- [x] 1.1 Baseline verde: `make test` (248) e `make lint` antes de tocar código.
- [x] 1.2 Caracterizar a saída ATUAL de `describe_modal_borrowing`: capturar a
  estrutura multi-origem (conjunto de origens, separador `||`) para um acorde de
  empréstimo, de modo a preservá-la (só a grafia muda).
- [x] 1.3 Escrever testes do ESTADO-ALVO (devem falhar hoje onde há `A#`):
  borrowing/campo em tom de bemóis grafa `Bb`/`Eb`/`Ab`, nunca `A#`/`D#`/`G#`.
- [x] 1.4 Teste: campo modal derivado de `build_scale` == tabela Chediak (reusar os
  modos de `modal-tonal-center`); inclui uma tônica bemol (ex.: Eb) sem grafia inválida.
- [x] 1.5 Teste: `build_functional_parse(symbols)` e `reharmonize_symbols(symbols)`
  (sem key) analisam contra o tom de `detect_key`, não de `guess_key`.

## 2. Spelling correto no empréstimo modal (frente ①)

- [x] 2.1 Adicionar o mapa chave-PT→modo-EN (`"maior"→"major"`, `"menor_natural"→
  "minor"`, `"menor_harmonica"→"harmonic_minor"`, `"menor_melodica"→"melodic_minor"`,
  `"dórico"→"dorian"`, `"frígio"→"phrygian"`, `"lídio"→"lydian"`, `"mixolídio"→
  "mixolydian"`, `"lócrio"→"locrian"`).
- [x] 2.2 Rotear `describe_modal_borrowing` e `_build_harmonic_field` por
  `Note`/`build_scale` (escala e notas soletradas), preservando a saída multi-origem.
- [x] 2.3 Testes 1.2–1.4 verdes; suíte completa verde.

## 3. Campo modal derivado — aposentar MODE_HARMONY (frente ②)

- [x] 3.1 Derivar (grau, qualidade) de `build_scale`/`_tetrad_quality` no
  `_build_harmonic_field`; remover dependência de `MODE_HARMONY`.
- [x] 3.2 Remover `constants.MODE_HARMONY`; remover `constants.MODES` e
  `harmony._transpose_note`/`_transpose_scale` quando ficarem órfãos.
- [x] 3.3 Suíte verde + ruff limpo.

## 4. Intervalo soletrado — aposentar normalize_note (frente ③)

- [x] 4.1 Delegar `HarmonicAnalysis._get_interval` a
  `interval_semitones(Note.parse(a), Note.parse(b))`; ajustar `validate_chord` para
  validar via `Note.parse` (sem `normalize_note`).
- [x] 4.2 Remover `HarmonicAnalysis.normalize_note` e `constants.NOTE_REPLACEMENTS`
  quando órfãos; conferir que nenhum import remanesce.
- [x] 4.3 Suíte verde (nenhum teste de função deve mudar — intervalo é invariante).

## 5. Detecção de tom unificada (frente ④)

- [x] 5.1 Em `functional_hmm.build_functional_parse` e
  `reharmonization.reharmonize_symbols`, trocar o fallback `guess_key` por
  `detect_key` (`.key_note`/`.mode`).
- [x] 5.2 Remover `HarmonicAnalysis.guess_key`.
- [x] 5.3 Teste 1.5 verde; suíte verde.

## 6. Verificação final

- [x] 6.1 `grep` confirma que `MODE_HARMONY`, `MODES`, `NOTE_REPLACEMENTS`,
  `normalize_note`, `guess_key`, `_transpose_scale/_transpose_note` não sobrevivem
  em `packages/`.
- [x] 6.2 `CHROMATIC_NOTES` só permanece se ainda tiver consumidor legítimo; senão
  remover.
- [x] 6.3 Suíte completa verde (≥248) + ruff limpo; saída de relatório grafando
  bemóis corretamente (verificação manual de uma música em tom bemol).
- [x] 6.4 `openspec validate finish-note-spelling` sem erros; pronto para archive.
