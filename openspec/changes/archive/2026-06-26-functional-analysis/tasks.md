# Tasks — functional-analysis

## 1. Rede de regressão
- [x] 1.1 Oráculo a partir do corpus + exemplos de Chediak (tom de Dó):
      `Bb7`→bVII7/subd. menor, `C7`/`F7`→blues, `B7`→VII7 cadencial vs `F#m7 B7`→V7/III.

## 2. Capability `harmonic-function`
- [x] 2.1 Formalizar grau→função (I/III/VI→T, II/IV→SD, V/VII→D) — confirmar
      `constants.HARMONIC_FUNCTIONS` contra a pág. 96.
- [x] 2.2 Adicionar **qualidade funcional** (forte/meio-forte/fraco): I,IV,V
      fortes; II,VII meio; III,VI fracos (pág. 92).
- [x] 2.3 Campo diatônico menor sobre 3 escalas (harmônica/natural/melódica
      real); `Vm7` natural sem função tonal (pp. 94–96).

## 3. Modificar `applied-dominant-analysis`
- [x] 3.1 Em `analyze_function`, **antes** de marcar `Dsec`/`SubV`, testar
      dom7-sem-função: `bVII7` (subd. menor), `I7`/`IV7` (blues), `VII7`
      (cadencial), `II7`/`bVI7` (subd. alterado).
- [x] 3.2 `VII7` contextual: cadencial (resolve direto no I, longo, sem II cad)
      vs `V7/III` (curto / clichê `IIIm … V7`).
- [x] 3.3 Garantir que o dominante secundário legítimo (`E7→Am` = V7/vi) segue
      detectado (sem regressão na spec existente).

## 4. Verificação
- [x] 4.1 Suíte verde; medir mudança de rótulos no corpus (quantos dom7 deixam
      de ser `Dsec` e viram função especial).
