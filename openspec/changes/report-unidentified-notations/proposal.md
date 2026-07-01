## Why

Uma notação em **posição de acorde** que o parser não identifica é hoje **descartada em
silêncio**, violando o princípio do projeto ("seções degradam VISÍVEIS, nunca em silêncio"). Dois
pontos de perda muda:

1. **Linha inteira some.** `classify_line` mede densidade por `is_chord_token` (fullmatch). Um
   token malformado (`D9/S` — baixo `/S` inválido) falha o fullmatch, derruba a densidade da linha
   abaixo do threshold, e a linha vira LYRIC → **todos** os acordes dela são descartados. Medido no
   corpus: `upa-neguinho` perdia quase toda a harmonia; a notação `X9/S` aparece **61×**.
2. **Chute silencioso.** Quando a linha é CHORD, `ChordPattern.find_all` casa só o prefixo válido
   (`D9` de `D9/S`) e joga fora o resto (`/S`) — extrai um acorde **adivinhado**, sem avisar.

Ambos contrariam "nunca chute" e "degrada visível". O usuário decidiu: notação não-identificada →
**coleta visível** (registra em `diagnostics`, continua a análise), com escopo **alvo** (só acorde
malformado — prefixo de acorde válido + resto que parece baixo/tensão inválido; poupa palavra de
letra).

## What Changes

- **Detecção de acorde malformado** (`cifra_core.lines.malformed_chord_token`): um token é
  malformado sse (a) NÃO é acorde completo (`is_chord_token` falso), (b) tem um **prefixo de acorde
  válido**, (c) o **resto começa com `/` ou `(`** (uma tentativa de baixo/tensão), e (d) sobra
  **lixo** depois de remover TODOS os acordes válidos e a decoração (`/`, `|`, `%`, `-`). O resíduo
  (d) evita o falso-positivo de acordes colados por barra (`Gm7(11)///Gb7(#11)///` = dois acordes
  válidos, resíduo vazio → NÃO malformado). O escopo (c) poupa letra (`Brasil` → resto `rasil` não
  começa com `/`/`(` → não é malformado).
- **Densidade conta o malformado como posição-de-acorde** (`classify_line`): uma linha dominada por
  `X9/S` volta a ser CHORD (recupera os acordes válidos que estavam nela, ex.: `E/D`, `D7(9)`).
- **Extração não chuta o malformado** (`extract_chords_from_lines`): um token malformado é
  **coletado** (via out-param `unidentified`) e **não** extraído (não emite o `D9` adivinhado). Os
  demais tokens seguem por `find_all` (zero regressão — barras coladas, baixos válidos e acordes
  colados intactos).
- **Coleta visível** (`analysis_service`): as notações não-identificadas entram em
  `result["diagnostics"]` (agregadas por token × contagem). Nada trava; a música é analisada com os
  acordes válidos.
- **NÃO-ESCOPO:** falha dura (o usuário escolheu coleta, não exceção); escopo estrito (qualquer
  não-acorde em linha CHORD); adivinhar o significado de `/S` (regra "nunca chute" — só reportamos).

## Capabilities

### Modified Capabilities
- `chord-line-classification`: a densidade conta tokens de **acorde malformado** como posição-de-
  acorde (para a linha não sumir), e a extração **detecta e não extrai** o malformado — coleta-o
  como notação não-identificada em vez de descartar em silêncio ou adivinhar um prefixo.
- `analysis-diagnostics`: notações não-identificadas em posição de acorde são **degradação
  visível** — registradas em `result["diagnostics"]`, nunca descartadas em silêncio.

## Impact

- **Código:** `cifra_core/lines.py` (helper + densidade + coleta na extração), `cifra_core/__init__`
  (export), `services/analysis_service.py` (fiar `unidentified` → `diagnostics`). NÃO toca o motor
  funcional, o `detect_key`, nem os gates.
- **Zero-regressão (medido, n=119):** a extração de acordes VÁLIDOS é idêntica exceto (a) os `X9`
  antes chutados de `X9/S` deixam de ser emitidos (agora reportados — comportamento desejado), e
  (b) o token colado `Gm7(11)///Gb7(#11)///` passa a extrair os dois acordes (correção). Nenhum
  outro acorde é perdido. Os **4 gates do baseline seguem 119/119**.
- **Regra de ouro:** "nunca chute" (o `/S` não é adivinhado, é reportado) + "degrada visível"
  (diagnostics). Transposição-invariante (a detecção é de forma, não de tom).
