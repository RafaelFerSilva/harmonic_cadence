## Why

A worklist de corroboração (n=170, `WORKLIST-ADJUDICATION.md`) mostrou casos alta-confiança de
**V-como-tônica** que o gate de qualidade do `detect_key` NÃO corrige: o K-S pega o **V** e a peça
tem um `V→I` limpo a repouso — mas a cadência está na **abertura**, não na janela final. O Path B
(`_anchored_resolution_path`) só varre a janela final (`_functional_dominant_resolves`,
`CADENCE_WINDOW`), então perde `a-volta` (`C7M Am7 Dm7 G7 C7M` — K-S=G, tônica=C, cadência no
início) e `dia-de-vitoria` (abre `A(add9)`, `E7→A`, K-S=E).

Uma relaxação ingênua (varrer a peça inteira) é **net-negativa** (medido): corrige 3 mas quebra 5,
incluindo 2 concordâncias existentes (`domingo-azul`, `esse-mundo-e-meu`, que abrem no IV mas
FECHAM na tônica real) e 2 casos onde o `detect_key` já acerta (`eh-menina`, `tempo-feliz`, que
abrem no IV/iv com uma tonicização passageira). Precisa de guardas Chediak-principiadas.

## What Changes

- **Novo Path C — cadencial (peça inteira), ADITIVO** ao gate de qualidade (`_tritone_gate`): os
  Paths A/B ficam **intactos** (preserva A Banda/Apesar/Menino do Rio verbatim). O Path C corrige
  `Y → X = (Y−7) mod 12` quando TODAS:
  1. **X é cadenciado ≥2×**: há **≥2** resoluções de `V7`/`SubV7` funcional (trítono) em `X` na peça
     inteira (baixo seguinte assenta em X) — a tônica é confirmada cadencialmente, não uma
     tonicização passageira do IV/iv (bloqueia `eh-menina`/`tempo-feliz`, com 1 só).
  2. **X é repouso predominante** (mesma guarda do Path B): maj/min em X > dominante, e ≥2.
  3. **X é o primeiro acorde** (âncora de abertura, mesma guarda do Path B).
  4. **A peça NÃO termina em Y como repouso**: se o último acorde parseável tem raiz Y e é
     maj/min, o K-S está confirmado como tônica (Chediak: repouso estrutural final) → aborta
     (bloqueia `domingo-azul`/`esse-mundo-e-meu`, que fecham na tônica real).
  5. **X ≠ Y**.
- **Medição (simulação n=170):** corrige **4** — `a-volta` (G→C ✓), `dia-de-vitoria` (E→A ✓) fecham
  a divergência; `atras-da-porta` (C#→F#, tônica certa) e `o-amor-e-chama` (B→E, modulante) mudam
  sem criar nem perder concordância. **Concordância de centro 121→123**, **zero regressão** das
  concordâncias, **4 gates de invariante 170/170**.
- **NÃO-ESCOPO:** os demais casos da worklist (K-S pegou o IV/ii/iii/relativa, ou a armadilha do
  ii-V) — geometrias diferentes, fora deste gate; ficam na worklist de curadoria.

## Capabilities

### Modified Capabilities
- `key-detection`: o gate de qualidade funcional ganha um **terceiro caminho (Path C)** que corrige
  o V-como-tônica quando a cadência `V→I` está na abertura (não na janela final), com guardas
  cadenciais (≥2 resoluções) e estruturais (X=1º acorde, peça não fecha em Y-repouso).

## Impact

- **Código:** só `domain/key_detection.py` (novo `_cadential_resolution_path` + fio no
  `_tritone_gate`). NÃO toca Paths A/B, `_i7_funk_anchor_path`, `_correct_parallel_mode`, nem o
  coder de função.
- **Zero-regressão (medido n=170):** concordância 121→123 (+2 limpos), nenhuma concordância
  perdida; 4 gates 170/170. Paths A/B intactos (A Banda etc. preservados por construção).
- **Regra de ouro:** discriminador FUNCIONAL do Chediak (tônica repousa e é cadenciada; V é
  tensão), transposição-invariante; medido contra o baseline funcional ao vivo; nunca `cc_key`.
