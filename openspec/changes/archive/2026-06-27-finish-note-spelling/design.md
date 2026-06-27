## Context

`domain/harmony.py` mantém um subsistema de nota legado, **sustenido-só**, baseado
em strings: `normalize_note` (via `NOTE_REPLACEMENTS`, que colapsa `Bb`→`A#`),
`_get_interval`, `_transpose_note`/`_transpose_scale` (sobre `CHROMATIC_NOTES`), e
o campo modal hardcoded `MODE_HARMONY`. Em paralelo, `cifra_core.theory` já oferece
o modelo soletrado: `Note` (letra + acidente, `pitch_class` derivada),
`interval_semitones`, e `build_scale` (grafia diatônica correta por construção,
cobrindo os 9 modos paralelos necessários — `major`, `minor`, `harmonic_minor`,
`melodic_minor`, `dorian`, `phrygian`, `lydian`, `mixolydian`, `locrian`).

O `_build_scale` da `HarmonicAnalysis` **já** usa `build_scale` (a escala principal
é soletrada certo). O resíduo legado vive só na descrição de **empréstimo modal** e
na aritmética de intervalo. Esta change finaliza a migração: uma fonte de verdade
de nota, conforme às specs `music-theory-core` e `key-detection` que já a exigem.

## Goals / Non-Goals

**Goals:**

- A saída "Origem do Empréstimo" grafar bemóis corretamente (`Bb`, `Eb`, `Ab`),
  conforme Chediak e a regra `music-theory-core` ("MUST NOT collapse flats").
- O campo modal vir **derivado** de `build_scale` (correto por construção), não de
  `MODE_HARMONY` hardcoded.
- Uma única detecção de tom (`detect_key`) em todos os entry points; `guess_key`
  aposentada.
- Aposentar `MODE_HARMONY`, `MODES`, `NOTE_REPLACEMENTS`, `normalize_note`,
  `_transpose_*`, `guess_key` sem regressão (suíte verde).

**Non-Goals:**

- **Não** atacar a Fase B (desambiguação maior↔relativa-menor) — é evolução, não
  migração; vem depois.
- **Não** refatorar a classe `HarmonicAnalysis` além do necessário para aposentar
  os símbolos.
- **Não** mexer em `cifra_core.theory` (já é a fonte correta).

## Decisions

**1. Mapa explícito chave-PT→modo-EN, não renomear as chaves legadas.**
`describe_modal_borrowing` itera modos paralelos com chaves PT (`"menor_harmonica"`).
`build_scale` usa nomes EN (`harmonic_minor`). Decisão: um dict de tradução local
(`{"maior":"major","menor_natural":"minor","menor_harmonica":"harmonic_minor", …}`),
mantendo os rótulos PT exibidos ao usuário (`MODE_NAMES_PT`) intactos. Alternativa
(reescrever tudo em EN): rejeitada — mudaria os rótulos visíveis sem necessidade.

**2. Derivar o campo modal de `build_scale` + `_tetrad_quality`.**
`modal.modal_field()` já faz exatamente isto para os modos de igreja. Reusar a mesma
mecânica (escala soletrada → tétrade por grau → qualidade) cobre também as paralelas
maior/menores. `MODE_HARMONY` vira redundante. Validar contra Chediak pp. 122-125
(cenários já existentes em `modal-tonal-center`).

**3. Intervalo via `interval_semitones(Note.parse(a), Note.parse(b))`.**
`_get_interval` passa a delegar ao `cifra_core.theory`. O resultado é idêntico para
notas válidas (a classe de altura é a mesma para `Bb` e `A#`), então **nenhum teste
de função deve mudar** — é troca de implementação, não de contrato. `normalize_note`
e `NOTE_REPLACEMENTS` deixam de ter uso e são removidos.

**4. `guess_key`→`detect_key` nos fallbacks standalone.**
`build_functional_parse(symbols, key=None)` e `reharmonize_symbols(symbols, key=None)`
passam a chamar `detect_key([...]).key_note/mode`. Realiza a regra já escrita em
`key-detection`. `guess_key` é removida.

**5. Testes de caracterização ANTES de remover o legado.**
Não há rede fixando a grafia de saída. Decisão: escrever primeiro os testes do
estado-alvo (borrowing devolve `Bb`; campo derivado == Chediak; tom standalone ==
`detect_key`), vê-los corretos, e só então migrar e apagar o legado. Test-first
porque o ganho é observável e fácil de regredir silenciosamente.

## Risks / Trade-offs

- **[`describe_modal_borrowing` é multi-origem]** lista *todos* os modos paralelos
  de onde o acorde poderia vir (`" || "`-separado). → Mitigação: caracterizar a
  saída multi-origem atual (estrutura, ordem) e preservá-la, mudando só a grafia das
  notas. Um teste compara o conjunto de origens antes/depois.
- **[Grafia de modos não-diatônicos exóticos]** `build_scale` aproxima a grafia de
  escalas não-heptatônicas; mas `describe_modal_borrowing` só itera os 9 modos
  heptatônicos paralelos, todos com grafia correta. → Sem exposição ao caso exótico.
- **[Acidente duplo em transposições distantes]** ex.: campo de um modo sobre tônica
  já alterada. → `Note`/`build_scale` suportam `bb`/`##`; caracterizar uma tônica
  bemol (ex.: Eb) garante que não há crash nem grafia inválida.
- **Trade-off:** a saída dos relatórios muda (A#→Bb). É **mudança desejada**, mas
  qualquer snapshot externo que dependa de `A#` quebraria. → Não há snapshots assim
  no repo; documentar no commit como mudança observável.

## Migration Plan

1. Adicionar testes de caracterização do estado-alvo (falhando onde hoje há `A#`).
2. Introduzir o mapa PT→EN e rotear `describe_modal_borrowing`/`_build_harmonic_field`
   por `build_scale` (soletrado). Rodar suíte.
3. Substituir o campo por derivação (`_tetrad_quality`); remover `MODE_HARMONY`.
4. Delegar `_get_interval` a `interval_semitones`; remover `normalize_note`,
   `NOTE_REPLACEMENTS`, `_transpose_note`/`_transpose_scale` e `MODES` quando órfãos.
5. `guess_key`→`detect_key` nos fallbacks; remover `guess_key`.
6. Suíte completa verde + ruff limpo; `openspec validate`.

Rollback: cada passo é commit-isolável; reverter o passo que regredir.

## Open Questions

- Algum rótulo PT do campo (`MODE_NAMES_PT`) precisa de ajuste fino ao derivar, ou a
  derivação preserva exatamente os mesmos nomes exibidos? (resolver no passo 2 com o
  teste de caracterização da estrutura de saída).
