# Protocolo de transcrição — ingest-songbook-vols-2-5

Regras operacionais dos lotes (D1–D6 do design). Cada música transcrita do PDF vira
`cifras/<slug>.md` e SÓ é admitida após `scripts/verify_transcription.py` passar.

## Página do livro (formato Chediak)

Cada música: título + compositor(es) no topo → bloco de DIAGRAMAS de acordes (o
vocabulário que o livro declara) → cifra com acordes sobre a letra (às vezes linha
`Introdução:` cifrada) → partitura (melodia) no restante/rodapé. Músicas podem ocupar
2+ páginas — conferir a continuação ANTES de fechar o arquivo (a página seguinte pode
ter só partitura = música acabou; ou mais cifra/coda = transcrever).

## O que entra no arquivo

1. **Header** (formato exato do corpus):
   ```
   ## <a name="<slug>"></a>🎼 <Título como impresso>

   **Compositores:** <como impresso na página>

   **Acordes Utilizados:** `X`, `Y`, `Z`, …
   ```
   O manifesto vem dos DIAGRAMAS (todos, na ordem impressa), NUNCA da própria cifra —
   senão a verificação é circular.
2. **Fence** (```) com a cifra: linhas de acordes (com os `/` de pulso como impressos)
   intercaladas com as linhas de letra. Linha `Introdução:`/coda cifrada entra. Os
   símbolos de acorde impressos NA PARTITURA (pauta) NÃO entram (duplicariam a
   progressão).
3. **Repetição:** `%`/`./.` no livro = repetir o acorde anterior → escrever o ACORDE
   explícito (a sequência alimenta cadência/progressão do motor).
4. **Tom:** o do livro, por construção (copiar os acordes impressos; nunca transpor).
   Não existe metadado `Tom:` no arquivo (o motor detecta dos acordes).

## Normalização de grafia (empilhados do livro → canônico do corpus)

| Livro (impresso)         | Arquivo (canônico)      |
|--------------------------|-------------------------|
| `C⁶₉` (6 sobre 9)        | `C6(9)`                 |
| `G⁷₄(b9)` (7 sobre 4)    | `G74(b9)`               |
| `A₄(9)`                  | `A4(9)`                 |
| `X⁷` etc. sobrescrito    | `X7`                    |
| `5+`/`#5` aumentado      | `X7(#5)` / `X7M(#5)`    |
| `add9`                   | `X(add9)`               |
| diminuto `º`/`O`         | `X°` (símbolo `°`)      |
| baixo `X/nota`           | igual (`C6(9)/G`)       |

Na dúvida entre grafias, consultar o vocabulário existente do corpus
(`grep -h "Acordes Utilizados" cifras/*.md`). `7M` = maior com 7ª maior; NUNCA trocar
qualidade na normalização (Eb7M ≠ Ebm7 — foi OCR mangling assim que corrompeu o v4).

## Admissão (gate)

```
uv run python scripts/verify_transcription.py cifras/<slug>.md
```
- `FALHA … faltam [...]` → acorde do diagrama ausente do corpo: RE-LER a página e
  corrigir a transcrição (hipótese nº 1 = erro meu). Não admitir até `ok`.
- `aviso … extras [...]` → acorde no corpo sem diagrama: re-conferir na página; se o
  livro realmente usa o acorde sem diagramá-lo, MANTER no corpo, ADICIONAR ao manifesto
  com a página anotada no relatório do lote (fato: diagrama omitido pelo livro).
- Página ilegível → música NÃO entra; registrar `[!]` na worklist com volume+página.

## Letra — opcional e dispensável (emenda 2026-07-02)

O motor só extrai linhas CHORD; a letra é contexto humano. FATO operacional: transcrever
letra integral de música famosa BLOQUEIA o agente no filtro de conteúdo (Águas de março
derrubou o lote 2.A duas vezes). Regra: **transcrever SOMENTE as linhas de acordes**
(com os `/` de pulso e a ordem/estrutura impressas; linha em branco entre sistemas;
`Introdução:`/`Coda:` mantidas). NO MÁXIMO 1–2 palavras-deixa por linha se precisar de
âncora de navegação. Anotar `letra omitida` na observação do lote. Os arquivos já
admitidos com letra ficam como estão.

## Regras duras

- NUNCA sobrescrever `cifras/<slug>.md` existente (colisão = parar e reportar).
- NUNCA transpor, NUNCA chutar acorde borrado (ilegível = pendência honesta).
- Offsets: Vol. 2 e Vol. 5 → **página do PDF = página do livro − 25**.
- Fronteira de lote: o lote é dono das músicas cujo TÍTULO está no seu intervalo de
  páginas PDF; a continuação pode passar do fim do intervalo (ler além só para fechar
  a música).
