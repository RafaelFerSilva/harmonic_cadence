## Why

A `modal-coloring-overlay` já detecta a coloração modal (`flavor`: mixolídio sobre maior,
frígio sobre menor) e a apresenta numa **seção separada** ("Coloração modal: traços
mixolídios…"). Mas o cabeçalho de centro ainda diz só "D maior" — o leitor precisa
costurar mentalmente "D maior" + "traços mixolídios" para chegar em **"D mixolídio"**, o
nome que um músico usaria. A informação existe; falta **promovê-la a um nome de modo** no
ponto onde o usuário lê o centro.

Esta é a parte **(A)** da arquitetura de bifurcação analítica decidida em explore (ver a
change irmã, bloqueada, `modal-center-arbitration`, que cobre a parte (B): a *anotação
curada* de Chediak para os casos de centro divergente — Arrastão dórico, Procissão
mixolídio — que a harmonia do Cifra Club não codifica). (A) e (B) compartilham a mesma
superfície de display e o mesmo princípio: **nunca tocam `detect_key`**.

Escopo destilado em explore, ancorado em Chediak (Vol. I, pp. 124-127) e na calibração já
existente do `modal_coloring`:
- **Mixolídio e frígio** têm assinatura mecânica que o parser já lê (`bVII→I`, `bII→i`) e
  o `detect_coloring` já emite → **promovê-los a nome de modo** ("D mixolídio", "D
  frígio") fundido ao centro detectado.
- **Eólio fica silencioso** (Chediak: eólio = menor natural; cadências eólias são
  subdominantes menores tonais comuns → nomeá-lo só inflaria a interface com o
  comportamento tonal padrão; o `modal_coloring` já o trata como controle/silêncio).
- **Dórico fica fora** — compartilha coleção com o mixolídio; separá-los sem melodia é
  impossível (Arrastão lê superfície mixolídia embora Chediak diga dórico). Dórico pertence
  à curadoria (B), não a (A).

## What Changes

- **Promoção do `flavor` a nome de modo no display:** quando `modal_coloring` está presente
  (mixolídio/frígio), o relatório passa a exibir o **centro nomeado pelo modo** — "D
  mixolídio" / "D frígio" — fundindo a tônica do `detect_key` (grafada pela `Note`) com o
  `flavor` já computado. A evidência (`bVII→I`, `bII→i`, posições) permanece como detalhe.
- **Função de rótulo** em `presentation/labels.py` (ex.: `modal_mode_name(key_note, flavor)
  -> "D mixolídio"`), reusando `scale_name`/`church_mode_pt` já existentes. É a única lógica
  nova; vive **inteiramente na camada de apresentação**.
- **Render** nos três alvos (`markdown.py`, `html.py`, `explain/prompt.py`): o nome de modo
  aparece junto ao centro; sem coloração, o cabeçalho tonal ("D maior") fica idêntico ao de
  hoje.
- **Apenas mixolídio/frígio** são nomeáveis (os flavors que o `detect_coloring` emite).
  Eólio silencioso, dórico fora — por construção, já que dependem do `flavor`, que nunca os
  produz.

**NÃO toca:** `detect_key`, `detect_coloring` (a lógica de detecção), `segment_keys`,
`TIE_BAND`, funções T/SD/D, cadências, nem qualquer métrica de baseline. É **promoção de
apresentação de um campo já computado** → baseline de tonalidade e coloração **idênticos**
por construção.

## Capabilities

### Modified Capabilities

- `analysis-reporting`: o cabeçalho/seção de centro passa a renderizar o **nome de modo
  grego** (mixolídio/frígio) fundido à tônica tonal quando a coloração modal está presente,
  preservando a leitura tonal e omitindo graciosamente quando ausente.

## Impact

- `presentation/labels.py` — nova função pura `modal_mode_name(key_note, flavor)` (reusa
  `scale_name`/`church_mode_pt`); sem estado, sem I/O.
- `presentation/reports/markdown.py` + `html.py` — render do centro nomeado pelo modo quando
  `modal_coloring` presente; cabeçalho tonal inalterado quando ausente.
- `explain/prompt.py` — incluir o nome de modo no prompt de explicação quando presente.
- **Testes:** unidade da função de rótulo (mixolídio/frígio → "X mixolídio"/"X frígio";
  flavor ausente/None → nome tonal puro); render presença/ausência; **paridade do baseline**
  (a 4-métrica Cifra-Club + centro estrutural + coloração **idênticos**).
- **NÃO toca** o domínio (`detect_key`/`detect_coloring`/`modal.py`) nem o JSON canônico de
  análise — a promoção é estritamente de display.
- **ROADMAP.md / AGENTS.md:** registrar (A) como concluída e a bifurcação (A)+(B) como a
  arquitetura de IA-explicável do modalismo (algoritmo nomeia o que detecta; curadoria anota
  o que o dado não codifica).
