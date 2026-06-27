## 1. Curadoria validada (scouting — feito)

- [x] 1.1 Curar lista ampla de MPB (Tom Jobim, Djavan, Chico, Caetano, Gil, Milton,
  Joao Bosco, Cartola, Vinicius...).
- [x] 1.2 Raspar de fato cada candidato; registrar tom Cifra Club, nº de acordes e
  resultado do `detect_key`.
- [x] 1.3 Descartar os que falham (`EmptyCifra`: Joao e Maria, Manha de Carnaval,
  Retrato em Branco e Preto) ou sem tom (O Bebado e o Equilibrista). Restam ~28.

## 2. Corpus ampliado no baseline

- [x] 2.1 Substituir a `GOLD` (Chediak, 9) pelo corpus Cifra-Club-keyed (~28 fatos
  `(artista, música, tom)`) em `scripts/key_baseline.py`.
- [x] 2.2 Atualizar o docstring/framing: ouro = Cifra Club (independente), **sem
  gap de transposição** → tônica-exata é métrica de primeira classe; remover a nota
  de "exata deprimida por transposição".
- [x] 2.3 Manter o relatório por-música (veredito exato/relativo/modo/ERRO) e a
  contagem de falhas de scrape.

## 3. Medir e verificar

- [x] 3.1 Rodar `uv run python scripts/key_baseline.py` (rede); confirmar n≈28 e
  capturar as três métricas frescas.
- [x] 3.2 Conferir que nenhuma cifra foi escrita em disco (só fatos no script).
- [x] 3.3 Suíte offline continua verde (`make test`) e `ruff` limpo — o gate
  sintético e a harness não mudaram.
- [x] 3.4 `openspec validate widen-key-corpus` sem erros; pronto para archive.
