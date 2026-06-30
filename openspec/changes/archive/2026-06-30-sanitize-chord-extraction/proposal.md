## Why

A extração de acordes é ruidosa: o regex canônico casa uma letra maiúscula `A–G` isolada
como acorde (a pilha de qualidades é `*` zero-ou-mais e o baixo é opcional), e o pipeline
roda essa extração sobre **toda** linha preservada — inclusive linhas de letra. Resultado:
palavras de letra viram acordes-fantasma (**B**rasil→`B`, **C**om→`C`, **D**esse→`D`,
"E"→`E`). Medido ao vivo no corpus local (`cifras/*.md`, n=62): **429 de 3015 tokens
extraídos (14%) são acordes de uma letra só**, e **277 linhas de prosa** sobrevivem ao
filtro injetando **409 tokens-fantasma**. Isso polui `detect_key` e o
`chediak_functional_center` — em **21/62 músicas o último acorde extraído (candidato a
tônica) é uma palavra de letra**. Todo o baseline é calculado sobre esse fluxo
contaminado; o invariante funcional (62/62) só sobrevive porque uma tríade-fantasma não é
trítono-dominante. O sinal de desambiguação é de **linha** ("esta linha inteira é cifra ou
letra?"), e esse classificador hoje não existe.

## What Changes

- **Classificador de linha por densidade** em `cifra_core`: uma função que rotula cada
  linha como CIFRA / LETRA / SEÇÃO pela razão *tokens-que-são-acorde-válido /
  total-de-tokens* (limiar ~0,6). `"C / / G / Am"` → CIFRA; `"Com seu Brasil"` → LETRA.
- **Confirmação de token por whitelist (opcional)**: a extração aceita um conjunto opcional
  de acordes conhecidos; um token de **uma letra só** (`A–G` pelado) só conta como acorde
  se estiver na whitelist. O vocabulário vem do header `Acordes Utilizados:` dos `.md` do
  corpus (e, no futuro, da lista de acordes do topo das páginas do Cifra Club).
- **Extração passa a ler só linhas de CIFRA**: o consumidor de acordes deixa de rodar o
  regex sobre linhas de letra. As linhas continuam preservadas em ordem (display intacto);
  só a *extração de acordes* fica seletiva.
- **Fiação**: `cifra_from_text` aceita e propaga a whitelist opcional; os scripts de
  baseline (`songbook_baseline.py`, `worklist_adjudication.py`) parseiam o manifesto e a
  passam.
- **NÃO-ESCOPO** (fases futuras): IR tipado `ParsedCifra`; suporte a ChordPro;
  conversão duas-linhas→ChordPro. Esta change é só classificador + whitelist.

## Capabilities

### New Capabilities
- `chord-line-classification`: classificação de cada linha como CIFRA/LETRA/SEÇÃO por
  densidade de acordes válidos, mais a confirmação opcional de tokens ambíguos (letra
  isolada `A–G`) contra um vocabulário conhecido; a extração de acordes consome essa
  classificação e lê só linhas de cifra.

### Modified Capabilities
- `cifra-core`: o padrão canônico de detecção de acorde deixa de tratar um token de **uma
  letra só** como acorde fora de contexto — passa a exigir contexto de linha-de-cifra
  e/ou confirmação por whitelist, estendendo o princípio que já vale para linhas de
  afinação ("os nomes de nota de uma letra NÃO são extraídos como acordes").

## Impact

- **Código:** `packages/cifra_core/src/cifra_core/lines.py` (novo classificador),
  `packages/cifra_core/src/cifra_core/chords.py` (regra do token ambíguo),
  `packages/cifra_core/src/cifra_core/ingest.py` (`cifra_from_text` recebe whitelist),
  `packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py`
  (`_extract_chords` lê só linhas de cifra), `scripts/songbook_baseline.py` e
  `scripts/worklist_adjudication.py` (parse do manifesto → whitelist).
- **Contrato:** `clean_cifra_lines` permanece idempotente e segue preservando linhas de
  letra na ordem (a classificação é leitura, não remoção). A API pública ganha funções
  novas e parâmetros **opcionais** — sem quebra.
- **Gate:** re-rodar `scripts/songbook_baseline.py` — invariante funcional **continua
  62/62** (base rochosa não regride), os ~429 fantasmas caem drasticamente, as 277 linhas
  de prosa deixam de contribuir tokens; `make test` verde, `make lint` limpo.
- **Regra de ouro preservada:** Cifra Club é só fonte; Chediak é a base; análise funcional
  invariante a transposição; medir contra o baseline ao vivo, nunca contra `cc_key`.
