## 1. Trava do baseline (antes de tocar código)

- [x] 1.1 Rodar `uv run python scripts/key_baseline.py` e registrar as 4 métricas Cifra-Club + centro tonal verbatim (referência de zero-regressão; deve ficar idêntico, pois `detect_key` não será tocado).
- [x] 1.2 Rodar `make test` e registrar a contagem verde atual (referência da suíte).
- [x] 1.3 Confirmar a citação de página em Chediak (`base_estudo/`) para "diminuto = V7(b9) sem fundamental"; anotar a página no design/relatório (nunca chutar).

## 2. Reconhecimento do dim7 como V7(b9) rootless (domínio)

- [x] 2.1 Em `domain/harmony.py`, adicionar um ramo dim7-específico em `analyze_function` (espelhando o ramo de dominante secundário) que dispara para `Category.DIMINISHED` com 7ª — SEM alterar `chord.is_dominant_seventh` nem o enum `Category`.
- [x] 2.2 Implementar o critério de resolução: alvo (raiz/baixo do próximo acorde) = `raiz_dim7 + 1` → dominante; fundamental implícita = `raiz_dim7 − 4`. Rotular primário (`V7(b9)` de I) ou secundário pelo grau do alvo (`V7(b9)/x`).
- [x] 2.3 Implementar o gate do diminuto de aproximação/passagem: sem resolução por semitom ascendente → NÃO dominante; reportar como diminuto de aproximação.
- [x] 2.4 Garantir que `B°7` continua `Category.DIMINISHED` e que `is_dominant_seventh` permanece `False` (a mudança é só na camada de função).

## 3. Função harmônica

- [x] 3.1 Em `harmonic_function.py`/`harmony.py`, atribuir função **D** ao dim7-dominante mesmo cromático (`#i°7`, `#ii°7`, `#iv°7`); manter o `vii°7` diatônico como D (já é).
- [x] 3.2 O diminuto de aproximação NÃO recebe função dominante.

## 4. Escala-acorde

- [x] 4.1 Em `chord_scale.recommended_scale`, mapear o dim7-dominante para a escala diminuta (octatônica) via `build_scale(root, "diminished")`, consistente com `G7(b9)`; o diminuto de aproximação mantém o tratamento atual (sem escala dominante).

## 5. Notação / relatório

- [x] 5.1 Confirmar que `roman.py` preserva `vii°7`/`#i°7` (a marca `°`), sem trocar o numeral.
- [x] 5.2 Adicionar a glosa funcional PT-BR no relatório (ex.: "`#i°7` = V7(b9)/ii — dominante rootless de ii"), degradando visível (`_safe_section`).

## 6. Testes

- [x] 6.1 `test_applied_dominants.py`: `B°7→C` = V7(b9) de I; `C#°7→Dm` = V7(b9)/ii; `F#°7→G` = V7(b9)/V (em C maior).
- [x] 6.2 Diminuto de aproximação/passagem (sem resolução semitom-acima) → NÃO dominante.
- [x] 6.3 `test_harmonic_function.py`: dim7-dominante cromático recebe função D; aproximação não.
- [x] 6.4 Escala diminuta: `B°7` dominante → escala diminuta; teste de que a octatônica bate com a do `G7(b9)` implícito.
- [x] 6.5 Anti-regressão de identidade: `B°7` continua `Category.DIMINISHED`, `is_dominant_seventh` False, numeral `vii°7` preservado.

## 7. Quality gate + docs

- [x] 7.1 `make test` verde; `make lint` limpo.
- [x] 7.2 Rodar `scripts/key_baseline.py` ao vivo; confirmar 4 métricas Cifra-Club + centro tonal IDÊNTICOS à task 1.1 (zero regressão — inegociável).
- [x] 7.3 Atualizar `ROADMAP.md` (marcar dim7-as-dominant feito; registrar que o baseline ficou idêntico) e citar a página de Chediak.
- [x] 7.4 `openspec validate dim7-as-dominant --strict` passa; pronto para `openspec archive`.
