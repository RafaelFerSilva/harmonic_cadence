## Why

A auditoria de completude do corpus (2026-07-02) encontrou **perda silenciosa de linhas
inteiras de acorde**: um token de acorde colado em barras de ritmo (`Am6/`, `Bm7/`,
`Bb7(9)///`) não passa em `is_chord_token` (fullmatch) **nem** em `malformed_chord_token`
(resíduo vazio o isenta, por design), então **não conta na densidade** de `classify_line`.
Linhas legítimas de acorde caem abaixo do threshold, viram LYRIC e são descartadas INTEIRAS
— perdendo até os acordes limpos da linha — **sem diagnóstico** (viola a degradação visível).

Medido no corpus (n=170): **11 músicas, 20 linhas, ~109 acordes perdidos hoje** (piores:
samba-em-preludio ≈27, dindi ≈26). A extração em si já resgata o token colado via
`find_all` quando a linha sobrevive — a spec `chord-line-classification` inclusive **promete**
extrair `Am7/` — mas a definição de densidade da mesma spec não conta esse token. O buraco é
espec-level: extração e classificação discordam sobre o que é "token de posição de acorde".

## What Changes

- **`classify_line` (cifra_core):** a definição de *chord-position token* para a densidade
  passa a incluir o token **acordes+decoração com resíduo vazio** — o mesmo critério que a
  extração já usa para resgatar (`Am7/`, `Bb7(9)///`, `Gm7(11)///Gb7(#11)///`, `B°/A/`).
  Extração e densidade voltam a concordar; a linha do dindi volta a ser CHORD.
- **Zero mudança na extração** (o resgate via `find_all` já existe e já é spec'ado) e zero
  mudança no motor de análise.
- **Re-medição obrigatória:** baseline funcional ao vivo (os 3 gates duros DEVEM seguir
  170/170; se um novo acorde recuperado violar um gate, é pausa-e-investiga, não força-verde)
  e re-materialização do corpus (`corpus build`) — números de corroboração de centro e do
  ledger de trítono (519) **podem mudar**, pois `razao-de-viver`/`velhos-tempos`/`dindi`
  ganham acordes de volta.
- Atualização dos números no AGENTS.md se mudarem.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `chord-line-classification`: a definição de *chord-position token* do requisito "Line
  classification by chord density" é ampliada para incluir tokens acorde+decoração de resíduo
  vazio (hoje só `is_chord_token` e `malformed_chord_token` contam) — alinhando a densidade à
  promessa de extração já existente na própria spec.

## Impact

- **Código:** `packages/cifra_core/src/cifra_core/lines.py` (`classify_line` / helper de
  densidade). Testes em `packages/cifra_core/tests/`.
- **Consumidores:** nenhum contrato muda (assinaturas idênticas); muda o VEREDITO de
  classificação de ~20 linhas reais — mais acordes chegam ao motor.
- **Corpus/baseline:** re-rodar `songbook_baseline.py` e `harmonic corpus build` + `report`;
  atualizar números documentados (concordância de centro, ledger) se moverem.
- **Risco controlado:** o critério resíduo-vazio já existe (é a cláusula (d) do
  `malformed_chord_token`, invertida) — não é heurística nova, é reuso da existente.
