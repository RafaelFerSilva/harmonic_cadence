## Why

O baseline de detecção de tonalidade roda contra n≈6 músicas reais — **ruído
estatístico**. Sem ampliar o corpus, qualquer ganho da Fase B (desambiguar
maior↔relativa-menor) fica indistinguível de flutuação. O índice do Chediak é
explícito: o corpus de validação deve ser **independente** ("vem do Cifra Club"),
não a Parte 4 do livro (direitos de terceiros, "não ingerir como fixtures").

A solução respeita a fronteira **e** melhora a medição: usar o **tom anotado pelo
próprio Cifra Club** como ouro. É a mesma fonte dos acordes, então **não há gap de
transposição** — a métrica de tônica-exata, antes deprimida e descartada, vira
honesta. E são apenas **fatos** (nome da música + tom público), sem armazenar cifra.

## What Changes

- Substituir a `GOLD` ancorada no Chediak (9 entradas, n≈6) por um corpus
  **ampliado** de ~28 músicas MPB anotadas com o **tom do Cifra Club**, todas
  validadas como rascáveis (curadas raspando de fato; as que falham — `EmptyCifra`,
  sem tom — ficam fora).
- Reposicionar o framing do `key_baseline.py`: com ouro = Cifra Club, **não há
  transposição**, então a tônica-exata é uma métrica de primeira classe (não mais
  "deprimida"). As três métricas (modo, exata, relativa-consciente) seguem.
- O corpus inclui **casos difíceis** (não cherry-pick): a varredura inicial expôs
  duas confusões sistemáticas — **relativa** (maior→relativa menor) e **paralela**
  (mesma tônica, modo trocado: Wave/Chega de Saudade/Valsinha). A paralela **não**
  estava no radar do roadmap; o corpus a torna mensurável.
- Nenhuma cifra é armazenada; o corpus é lista de fatos `(artista, música, tom)`,
  re-scrapada a cada execução (rede).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `key-accuracy-evaluation`: adiciona que o baseline de músicas reais usa o **tom
  da própria fonte (Cifra Club) como anotação-ouro independente** — sem gap de
  transposição, tornando a tônica-exata significativa — e que o corpus é uma lista
  de **fatos** committada `(artista, música, tom)`, sem armazenar cifras.

## Impact

- **Código:** `scripts/key_baseline.py` (corpus + framing). Sem mudança na harness
  (`validation/key_accuracy.py`) nem no gate offline sintético (`test_key_corpus.py`).
- **Medição:** n salta de ~6 para ~28; tônica-exata vira honesta; expõe a confusão
  paralela como segundo alvo de Fase B.
- **Copyright:** dentro da fronteira — corpus independente do Cifra Club, fatos
  apenas, cifras não armazenadas (alinha o `key_baseline.py` à diretiva do índice).
- **Testes/CI:** offline inalterado (a suíte não tem rede; o baseline é script de
  rede, fora do pytest).
