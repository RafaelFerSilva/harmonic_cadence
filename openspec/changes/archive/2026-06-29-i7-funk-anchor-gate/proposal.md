## Why

O único buraco de centro estrutural restante (baseline **18/19**) é **Aquele Abraço**
(Gilberto Gil): tônica funk **I7** em Mi, que o `detect_key` lê como **Lá**. A música é um
vamp funk **I7-IV7** (`E7(9)↔A7(13)`); o IV (Lá) é mais frequente (43× vs 21×) e descansa
como tríade, então o K-S confiante pega o IV (A maior 0.8943; E maior 2º, 0.7516 — gap 0.14,
fora da `TIE_BAND` 0.10, então a corroboração cadencial nem entra).

O gate de qualidade existente **não** alcança o caso: ele corrige "K-S pegou o **V** → desce
5ª (Y−7)". Aqui a geometria é **inversa** — a tônica real Mi é o **V de Lá** (uma 5ª *acima*
do palpite; Lá = IV de Mi) — e a tônica soa como dominante (I7), violando a premissa do gate
("tônica repousa, V é tensão"). Não há cadência V→I a Mi (`B7→A`, nunca `B7→E`): sinais
estatísticos e funcionais apontam todos para Lá. O que **codifica** Mi é estrutural: a peça
**abre e fecha em Mi**.

## What Changes

- Adicionar ao `detect_key` um **caminho de âncora I7-funk** — novo, ortogonal ao gate de
  trítono — que corrige o palpite K-S `Y` para `X` quando **todas** estas guardas valem
  (cada uma codifica uma propriedade do I7-funk, não a música-exemplo):
  1. **abre e fecha em X**: `first_chord_root == last_chord_root == X`;
  2. **K-S pegou o IV de X**: `Y == (X + 5) mod 12` (assinatura do vamp I7-IV7);
  3. **X soa como dominante**: aparece como `X7` em algum ponto (a tônica I7 funk);
  4. **X também repousa**: aparece como **tríade maior** em algum ponto (é tônica de verdade,
     não um pedal de V — onde X só apareceria como `X7`);
  5. **X é plausível**: está entre as **alternativas top-2** do K-S.
- A correção é **ultraconservadora** (como o resto do gate): só dispara sob a conjunção
  estrita das 5 guardas. Geometricamente separada dos caminhos existentes (sobe 5ª, ancorada
  em first==last), sem interação com eles (que descem 5ª).

## Capabilities

### New Capabilities
<!-- Nenhuma: estende uma capability existente. -->

### Modified Capabilities
- `key-detection`: o `detect_key` passa a corrigir o centro quando o K-S pega o **IV** de uma
  tônica funk **I7** que abre e fecha a peça — um caminho distinto do gate de "V-como-tônica"
  (geometria inversa). Recupera o centro estrutural de peças I7-IV7 (Chediak XXXIV).

## Impact

- **Código afetado:** `packages/harmonic_analysis/.../domain/key_detection.py` — novo helper
  (ex. `_i7_funk_anchor_path`) e sua chamada no `detect_key`, após `_tritone_gate`, com
  acesso ao `ranked` (para a guarda 5, top-2). Testes em `test_tritone_gate.py` /
  `test_tonal_center_detection.py`.
- **Não toca** o K-S nem a corroboração cadencial; é só uma correção de centro pós-K-S, no
  mesmo lugar do gate de trítono.
- **Validação:** simulação read-only contra o corpus `scripts/key_baseline.py` (n=60) feita
  **antes** de codar — o gatilho base (guardas 1+2) dispara em **1/60** (Aquele Abraço) e
  **ajuda** (X=E=gold); **zero quebras, zero falsos-positivos**. Trava: zero regressão das
  ~41 corretas (alvo: modo 86 · exata 74 · relativa 81 · coleção 97 · **centro 18/19→19/19**).
- **Caveat honesto:** ajusta-se a **n=1** no corpus; risco residual = falso-positivo numa peça
  *futura* que abra+feche no V do tom real, mitigado pelas guardas 3–4 (X repousa como tríade
  **e** soa como dominante — um pedal de V puro não satisfaz ambas). Documentado.
- **Citação:** Chediak XXXIV (I7/IV7 blues/funk — a 7ª sobre a tônica é função especial, não
  dominante).
