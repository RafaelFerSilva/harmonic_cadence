## 0. Trava de baseline (ANTES de qualquer código)

- [x] 0.1 Rodar `uv run python scripts/key_baseline.py` e registrar as 4 métricas
  Cifra-Club + centro estrutural + modulantes **verbatim** (referência de zero-regressão).
- [x] 0.2 Confirmar por sondagem ao vivo (rede) quais músicas do corpus já disparam
  `modal_coloring` (mixolídio: Upa Neguinho/Ponteio; frígio: Canto de Ossanha) — são os
  alvos que (A) vai nomear; registrar o estado atual do display delas.

## 1. Função de rótulo (presentation/labels.py)

- [x] 1.1 Adicionar `modal_mode_name(key_note: str, flavor: str) -> str` que funde a tônica
  tonal (grafada pela `Note`) com o modo grego do `flavor`, reusando `scale_name`/
  `church_mode_pt` (ex.: `("D", "mixolydian") -> "D mixolídio"`; `("D", "phrygian") ->
  "D frígio"`).
- [x] 1.2 Só mixolídio/frígio são nomeáveis (os flavors que `detect_coloring` emite); para
  flavor ausente/None/desconhecido, retornar o nome tonal puro (sem inventar modo). Não
  introduzir eólio nem dórico aqui — eles nunca chegam como `flavor`.

## 2. Render do centro nomeado (relatórios)

- [x] 2.1 Em `presentation/reports/markdown.py`: quando `analysis["modal_coloring"]` presente,
  exibir o centro como **nome de modo** ("Centro: D mixolídio") junto à leitura tonal,
  mantendo a seção de coloração existente como detalhe de evidência (`bVII→I`, posições).
- [x] 2.2 Em `presentation/reports/html.py`: paridade com o markdown.
- [x] 2.3 Sem `modal_coloring`: o cabeçalho de centro fica **byte-idêntico** ao de hoje
  ("D maior").
- [x] 2.4 Em `explain/prompt.py`: incluir o nome de modo no prompt quando presente.

## 3. Testes (offline, determinísticos)

- [x] 3.1 `test_modal_mode_naming.py` (ou estender `test_pt_br_localization`): unidade de
  `modal_mode_name` — mixolídio/frígio → "X mixolídio"/"X frígio"; bemóis grafados certo
  (`Bb` → "Sib …"); flavor None/desconhecido → nome tonal puro.
- [x] 3.2 Render: análise com `modal_coloring` mixolídio mostra "D mixolídio" no centro;
  análise sem coloração mostra "D maior" inalterado (markdown + html).
- [x] 3.3 Anti-regressão de schema: o JSON canônico de análise (`key`/`mode`/
  `modal_coloring`) permanece inalterado — a promoção é só de display.

## 4. Validação ao vivo + paridade (rede)

- [x] 4.1 Re-rodar `scripts/key_baseline.py`: as 4 métricas + centro estrutural + modulantes
  **idênticos** ao 0.1 (a change não toca detecção).
- [x] 4.2 Sondagem ao vivo: Upa Neguinho/Ponteio renderizam "… mixolídio"; Canto de Ossanha
  "… frígio"; as eólias de controle (Wave/Corcovado/Insensatez/Construção) seguem com
  cabeçalho tonal puro (silêncio preservado); Arrastão segue lido como "D maior" + superfície
  mixolídia (o dórico de Chediak é trabalho da change (B), não desta).

## 5. Docs

- [x] 5.1 `make test` + `make lint` verdes.
- [x] 5.2 Atualizar `ROADMAP.md`/`AGENTS.md`: (A) concluída (promoção de nome de modo); a
  bifurcação (A) algoritmo + (B) curadoria registrada como a arquitetura de IA-explicável do
  modalismo. `openspec archive modal-mode-naming` após o merge.
