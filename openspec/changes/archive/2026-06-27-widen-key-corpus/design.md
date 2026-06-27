## Context

Há três mecanismos de corpus no projeto:
1. **Sintético** (`test_key_corpus.py`): 12 progressões textbook, offline, é o gate
   de regressão (≥90%, hoje 100%). Sem copyright.
2. **GOLD baseline** (`key_baseline.py`): músicas reais com tom **Chediak**,
   re-scrapado; n≈6 (9 listadas, ~3 falham). Tem o gap de transposição.
3. **`load_corpus(data/)`**: usa o tom do Cifra Club, mas `data/` é gitignored →
   não-durável.

O índice do Chediak (`base_estudo/`) proíbe ingerir a Parte 4 (≈80 músicas
analisadas) como dados/fixtures e diz que o corpus deve vir do Cifra Club,
independente. A decisão (confirmada): **ouro = tom do Cifra Club**.

## Goals / Non-Goals

**Goals:**

- Ampliar o baseline de músicas reais de n≈6 para n≈28, dentro da fronteira de
  copyright.
- Tornar a tônica-exata uma métrica honesta (sem transposição), ancorando o ouro na
  mesma fonte dos acordes.
- Corpus reproduzível: lista committada de fatos `(artista, música, tom)`, sem
  cifras.

**Non-Goals:**

- **Não** atacar a Fase B em si (desambiguação) — isto só destrava a *medição*.
- **Não** mexer no gate sintético offline nem na mecânica da harness.
- **Não** armazenar cifras (mantém a fronteira; o corpus re-scrapa).
- **Não** usar o tom do Chediak como ouro (decisão: Cifra Club).

## Decisions

**1. Ouro = tom do Cifra Club (a mesma fonte dos acordes).**
Elimina o gap de transposição: a tônica-exata passa a medir detecção real, não
diferença de arranjo. Endossado pelo índice ("corpus independente"). Alternativa
(Chediak): autoritativo, mas copyright-sensível e com transposição — rejeitada
para este corpus de *medição* (o Chediak segue como árbitro **teórico**, não como
gold de baseline).

**2. Curar raspando de fato; descartar o que não scrapa.**
A lista de candidatos foi raspada antes de fixar; `EmptyCifra` (só-letra) e sem-tom
ficam fora. Garante que n≈28 é real, não aspiracional. As que entram foram
verificadas: tom presente, acordes extraídos, `detect_key` roda.

**3. Incluir casos difíceis — sem cherry-pick.**
O corpus inclui as confusões expostas pela varredura (relativa **e** paralela). Um
baseline que só inclui acertos mente. A confusão paralela (Wave Dm→D, etc.) emergiu
do corpus e vira um segundo alvo de Fase B antes invisível.

**4. Fatos committados, cifras não.**
O corpus é `(artista, música, tom)` no script — fatos públicos, não-copyrightáveis.
A cifra é buscada em tempo de execução e descartada. Mantém a diretiva do projeto.

**5. Sem novo teste offline.**
A suíte pytest é offline (sem rede); o baseline é script de rede. Medir músicas
reais em CI exigiria cifras em cache (proibido). O gate de regressão continua sendo
o corpus **sintético**; o baseline real é ferramenta de medição manual.

## Risks / Trade-offs

- **[O tom do Cifra Club é crowd-sourced]** pode rotular errado (ex.: ancorar numa
  seção). → Mitigação: é a anotação *declarada* da fonte; divergências viram dados
  (a confusão paralela é em parte isso). Para teoria, o Chediak continua árbitro.
- **[Scrape flaky / Cifra Club muda]** n pode encolher ou um tom mudar entre runs.
  → Mitigação: o tom-ouro fica committado como fato; se o scrape retornar outro tom,
  a divergência é detectável. O script já reporta falhas por música.
- **Trade-off:** medição mais ampla e honesta vs. perda da autoridade teórica do
  ouro. Aceito: o baseline mede *detecção*, não *teoria*; o Chediak governa a teoria.

## Open Questions

- Vale, num passo futuro, anotar a confusão (relativa vs paralela vs erro) por
  música no output do baseline, para o alvo da Fase B ficar quantificado por tipo?
  (fora de escopo aqui; candidato a follow-up).
