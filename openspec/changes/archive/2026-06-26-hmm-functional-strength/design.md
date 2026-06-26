# Design — Emissão do HMM ponderada pela força funcional (Chediak, pág. 92)

## Mecanismo

A emissão atual: `PRIMARY_MASS` (0.70) para a macro determinística, `1 - 0.70`
espalhado nas alternativas via `ALT_PRIORS`. A mudança torna a massa primária
função da **força** do grau (Chediak, pág. 92), propagando pela cadeia (Viterbi +
forward-backward), em vez de aplicar um ajuste pós-hoc na confiança.

```
STRENGTH_MASS = {
    "strong": 0.82,   # I, IV, V — âncoras: confia mais no rótulo
    "medium": 0.70,   # II, VII — substitutos meio-fortes (= padrão atual)
    "weak":   0.55,   # III, VI — substitutos fracos: mais massa às alternativas
    None:     0.70,   # sem grau diatônico / parse só-código: padrão (sem regressão)
}
```

`None → 0.70` é deliberado: um parse a partir de códigos de função (sem força)
emite exatamente como antes — garante zero regressão na ponte `parse_codes`.

## De onde vem a força

- `build_functional_parse(harmonic_analysis)`: lê `e["strength"]` de cada acorde
  (já presente desde o wiring de relatório).
- `parse_progression(symbols, key, mode)`: deriva a força do grau via
  `functional_strength(get_degree(chord))`.

## Por que ponderar a emissão (e não a confiança final)

A força é uma propriedade do **rótulo determinístico** (quão confiável ele é).
Ponderar a emissão deixa essa confiabilidade fluir pela gramática de transição:
um acorde fraco não só fica menos confiante, como abre espaço real para o caminho
de Viterbi escolher outra macro quando o contexto puxa. Um ajuste pós-hoc não
teria esse efeito estrutural.

## Não-objetivos

- Não toca transições, estados, nem a estrutura do Viterbi/forward-backward.
- Os valores de `STRENGTH_MASS` são calibráveis; ficam como ponto de ajuste
  futuro contra um corpus anotado.
