## Context

`segment_keys` segmenta a sequência de acordes em regiões tonais usando janelas não-sobrepostas de 8 acordes, fundindo blocos adjacentes de mesma tonalidade. Window=8 é conservado deliberadamente — detecta modulações curtas. O problema é o pós-processamento: sem filtro, Wave produz 21 regiões (muitas com 4% dos acordes), o que é ilegível para o usuário e não útil para métricas.

Paralelamente, o gold do baseline (`key_baseline.py`) usa um único `(artista, música, tom)` por entrada. Wave e Chega de Saudade têm gold "Dm", que o sistema acerta — mas pela Fase B v2 (inversão por qualidade de tônica), não por detectar a estrutura bipartida. A medição mascara a fraqueza.

## Goals / Non-Goals

**Goals:**
- Pós-processar `segment_keys` numa função `dominant_regions` que produz 2–4 regiões limpas, sem alterar o comportamento de `segment_keys`.
- Usar `dominant_regions` em `analysis_service` para popular `tonal_regions` nos resultados.
- Estender o harness `key_accuracy.py` para aceitar gold multi-região `(primary, secondaries)`.
- Atualizar `key_baseline.py` para marcar Wave e Chega de Saudade como modulantes e usar a nova métrica.

**Non-Goals:**
- Alterar `segment_keys`, `detect_key`, `TIE_BAND` ou qualquer lógica de detecção.
- Mudar o `KeyEstimate` pontual retornado por `detect_key` para a música inteira.
- Cobrir outros tipos de modulação além do que já `segment_keys` detecta.
- Identificar automaticamente quais músicas são modulantes (isso é curadoria manual do corpus).

## Decisions

### D1 — Algoritmo de `dominant_regions`: fusão por peso acumulado, não por limiar rígido

A função recebe a lista de `KeyRegion` e o total de acordes. Itera fundindo regiões adjacentes de mesma tonalidade (que `segment_keys` às vezes fragmenta quando a janela cai na fronteira errada), depois remove iterativamente a menor região enquanto ela tiver menos que `min_pct` do total, redistribuindo seus acordes para a vizinha de mesma tonalidade (se existir) ou para a vizinha mais próxima em score K-S.

```
Antes (Wave, 21 regiões):
  D minor 4%, G major 12%, B major 4%, D major 4%, B major 4%,
  D minor 4%, ... (17 regiões mais, cada uma ~4%)

Depois (dominant_regions, min_pct=0.10):
  D minor  ~20%   (regiões menores de Dm fundidas)
  G major  ~24%   (regiões de G major fundidas)
  D major  ~24%   (regiões de D major fundidas)
  ... ≤4 regiões
```

Alternativa descartada: limiar fixo de número máximo de regiões (ex.: top-3 por peso). Problema: descarta informação estrutural em peças longas onde 4+ regiões são legítimas.

### D2 — Gold multi-região: tupla `(primary, secondaries_list)` em `key_baseline.py`

O formato mais simples que estende sem quebrar o corpus existente:
```python
# Monotonal (status quo):
("Tom Jobim", "Garota de Ipanema", "F")

# Modulante (novo):
("Tom Jobim", "Wave",             "Dm", ["D"])
("Tom Jobim", "Chega de Saudade", "Dm", ["D"])
```
O script trata entradas com 4 elementos como modulantes. O harness `key_accuracy.py` recebe um novo tipo `MultiKeyEval` com campos `primary_ok`, `all_ok`, `detected_keys`.

Alternativa descartada: arquivo JSON separado para o gold multi-região. Adiciona complexidade de manutenção sem ganho — o corpus ainda é pequeno.

### D3 — `dominant_regions` exportada de `key_detection.py`, não de `analysis_service`

A função é pura (não precisa de contexto de análise) e testável isoladamente. Colocar em `key_detection.py` mantém toda a lógica de detecção/segmentação no mesmo módulo. O `analysis_service` apenas chama `dominant_regions(segment_keys(symbols), len(symbols))`.

### D4 — `min_pct=0.10` como padrão, recalibrável

10% de 100 acordes = 10 acordes = ~1 janela + resto. Cobre o caso de Wave (regiões de 4% são ruído) sem suprimir regiões genuínas de músicas mais curtas. O parâmetro é exposto para facilitar recalibração futura com o corpus crescendo.

## Risks / Trade-offs

- **Risco: `dominant_regions` suprime uma modulação real curta.** Mitigação: min_pct=0.10 é conservador — 10% de uma música de 60 acordes = 6 acordes, suficiente para uma frase modulante. Músicas com modulações mais curtas devem usar `segment_keys` diretamente.

- **Risco: gold multi-região aumenta a complexidade do baseline sem melhorar os números.** Mitigação: esse é o ponto — a mudança visa tornar a medição mais honesta, não inflacionar a acurácia. O ROADMAP registra explicitamente que o acerto atual de Wave/Chega é "pela razão errada".

- **Trade-off: curadoria manual das músicas modulantes.** Identificar automaticamente quais músicas têm modulações reais exigiria um critério de "região secundária significativa" — que é exatamente `dominant_regions`. Poderia ser automatizado no baseline no futuro, mas hoje é mais seguro anotar manualmente as duas casos conhecidos.

## Open Questions

- Após a implementação, há outras músicas no corpus n=60 que também modulam e deveriam ter gold multi-região? (Wave e Chega de Saudade são os casos identificados — verificar durante a tarefa de validação.)
- O campo `tonal_regions` no JSON de saída deve incluir o atributo `is_dominant: true/false` para distinguir regiões brutas de dominantes? (Decisão deferida — por ora o resultado já usa `dominant_regions`.)
