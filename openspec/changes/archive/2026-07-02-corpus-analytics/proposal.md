## Why

O corpus persistido (`persist-analysis-corpus`) existe mas está parado: o banco DuckDB disseca
as 170 análises e só responde duas consultas (ledger de centro, bigrama de função). O projeto
nunca pôde perguntar nada sobre a MPB **como conjunto** — distribuição real das cadências de
Chediak, as "frases" funcionais recorrentes, vocabulário por modo, onde vivem os dominantes
secundários. É o "medir em vez de achar" subindo à escala de corpus, com custo baixo (tudo é
view SQL sobre fatos já materializados). Além do valor musicológico próprio, o relatório é o
**insumo empírico** da adjudicação pendente do ledger de trítono (519 ocorrências): agrupar por
padrão transforma 519 casos soltos em ~dezenas de padrões adjudicáveis.

## What Changes

- **Novas views de analytics** em `persistence/views.sql` (estatística descritiva, zero
  mudança no motor): distribuição de cadências por família (contagem e músicas), trigramas de
  função (as "frases" — ex. `T→SD→D`), vocabulário de qualidades/acordes por modo detectado,
  densidade de dominantes secundários (`Dsec`/`Daux`/`Dext`/`SubV*`) por música, e o **ledger de
  trítono agrupado por padrão** (`function_code × degree × qualidade`, com contagem e exemplos)
  — a worklist de 519 vira padrões adjudicáveis.
- **Novo comando CLI** `harmonic corpus report`: consulta as views e gera um relatório
  musicológico em **Markdown** (seções: corpus, cadências, progressões, vocabulário,
  secundários, ledger de curadoria), gravado em arquivo — legível por humano e versionável se o
  usuário quiser.
- **Nada de ML**, nada de acurácia: estatística descritiva sobre a SAÍDA do motor. O relatório
  nunca compara motor×banco como placar (o banco é view materializada, não ouro).

## Capabilities

### New Capabilities
- `corpus-analytics-report`: views de analytics musicológicos sobre o corpus persistido e o
  comando `corpus report` que as consolida num relatório Markdown descritivo.

### Modified Capabilities
<!-- Nenhuma: as views existentes (gates, ledgers) não mudam de requisito; as novas views e o
     relatório são aditivos e vivem na capability nova. -->

## Impact

- **Código:** `persistence/views.sql` (novas views), novo módulo
  `persistence/report.py` (consulta views → Markdown), CLI `cli/main.py` (ação `report` no
  subcomando `corpus` existente). Sem nova dependência (DuckDB já presente); sem tocar
  `domain/`/`services/`.
- **Pré-requisito de uso:** banco populado (`harmonic corpus build`); o comando falha visível
  se vazio (mesmo padrão do `corpus gates`).
- **Relatório:** arquivo Markdown gerado localmente (ex. `corpus-report.md`); não versionado
  por padrão (deriva do corpus gitignored — regenerável).
- **Frente A (adjudicação):** a seção "ledger por padrão" é o insumo direto da futura change de
  adjudicação Chediak dos 519.
