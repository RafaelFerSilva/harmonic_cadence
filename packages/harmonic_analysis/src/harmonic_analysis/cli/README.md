# Harmonic Cadence CLI

Interface de linha de comando para análise harmônica de músicas brasileiras.

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/harmonic-cadence.git
cd harmonic-cadence

# Instale com uv
uv sync
```

# Comandos disponíveis no Harmonic CLI

## 1 - analyze - Análise harmônica de músicas

Realiza análise harmônica de uma música específica ou de todas as músicas de um artista.

Sintaxe básica:

    uv run harmonic analyze ARTISTA [MÚSICA] [OPÇÕES]
Opções:

--all: Analisa todas as músicas do artista (não especifique o nome da música quando usar esta opção)

--format ou -f: Formato do relatório (valores aceitos: html, json, markdown - padrão: json)

Exemplos:
```
# Analisar uma música específica
uv run harmonic analyze "Djavan" "Flor de Lis" --format html

# Analisar todas as músicas de um artista
uv run harmonic analyze "Djavan" --all --format markdown
```


## 2. cache - Gerenciamento de cache
Baixa e armazena músicas localmente para uso offline.

Sintaxe básica:

    uv run harmonic cache [OPÇÕES]

Opções:

--songs: Lista de músicas no formato artista:música (pode especificar múltiplas)

--file ou -f: Arquivo contendo lista de músicas (uma por linha, formato: artista:música)

--artist ou -a: Nome do artista para baixar todas as músicas

--force: Força o download mesmo se a música já existir no cache

Exemplos:

```
# Baixar músicas específicas
uv run harmonic cache --songs "Djavan:Flor de Lis" "Djavan:Azul"

# Baixar todas as músicas de um artista
uv run harmonic cache --artist "Djavan"

# Baixar músicas de um arquivo
uv run harmonic cache --file musicas.txt
```

## 3. list - Listagem de músicas
Lista as músicas disponíveis de um artista, podendo mostrar apenas as em cache.

Sintaxe básica:

    uv run harmonic list ARTISTA [--cached] [--all]
Opções:

--cached: Lista apenas músicas disponíveis no cache local

Exemplos:
```
# Listar todas as músicas do artista (online)
uv run harmonic list "Djavan"

# Listar apenas músicas em cache
uv run harmonic list "Djavan" --cached
```

### Observações importantes:
O comando analyze requer ou um nome de música específico ou a flag --all para analisar todas as músicas.

No comando cache, você pode usar múltiplas formas de especificar as músicas (arquivo, lista direta ou por artista).

O formato padrão para relatórios é JSON, mas você pode escolher entre HTML ou Markdown.

## Outros exemplos

### Análise básica (formato JSON padrão)
    uv run harmonic analyze "Djavan" "Sina"

### Especificando formato HTML explicitamente
    uv run harmonic analyze "Djavan" "Sina" --format html

### Análise com saída em Markdown
    uv run harmonic analyze "Chico Buarque" "Construção" --format markdown

### Para analisar todas as músicas:
    uv run harmonic analyze "Djavan" --all --format json

### Para analisar uma música específica:
    uv run harmonic analyze "Djavan" "Flor de Lis" --format html

### Se esquecer de especificar:
    uv run harmonic analyze "Djavan"


Exemplos com Diferentes Artistas

```
# João Gilberto
uv run harmonic analyze "Joao Gilberto" "Chega de Saudade"

# Caetano Veloso
uv run harmonic analyze "Caetano Veloso" "Sampa"

# Tom Jobim
uv run harmonic analyze "Tom Jobim" "Garota de Ipanema"

# Chico Buarque
uv run harmonic analyze "Chico Buarque" "Construção"
```

## Cache de Músicas
O CLI permite baixar e cachear músicas para uso offline.

### Cachear uma única música
    uv run harmonic cache --songs "Djavan:Sina"

### Cachear múltiplas músicas
    uv run harmonic cache --songs "Djavan:Sina" "Tom Jobim:Garota de Ipanema" "Chico Buarque:Construção"

### Forçar atualização do cache
    uv run harmonic cache --songs "Djavan:Sina" --force

## Usando Arquivo de Lista
Você pode criar um arquivo musicas.txt com a lista de músicas para análise:


```
# text
Djavan:Sina
Tom Jobim:Garota de Ipanema
Chico Buarque:Construção
Caetano Veloso:Sampa
```


E então usar o comando:

    uv run harmonic cache --file musicas.txt


# Listar músicas de um artista
    uv run harmonic list "zeca pagodinho" --all

# Listar apenas músicas em cache
    uv run harmonic list "zeca pagodinho" --cached

# Baixar todas as músicas de um artista
    uv run harmonic cache --artist "zeca pagodinho"

# Forçar download de todas as músicas (mesmo que já existam em cache)
    uv run harmonic cache --artist "zeca pagodinho" --force

## Ajuda

```
# Ver todos os comandos disponíveis
uv run harmonic --help

# Ajuda específica do comando analyze
uv run harmonic analyze --help

# Ajuda específica do comando cache
uv run harmonic cache --help
```



## Exemplos de Workflow
### Workflow Básico

```
# 1. Baixar música para cache
uv run harmonic cache --songs "Djavan:Sina"

# 2. Analisar a música
uv run harmonic analyze "Djavan" "Sina"
```

## Workflow com Múltiplas Músicas
```
# 1. Criar arquivo de músicas
echo "Djavan:Sina
Tom Jobim:Garota de Ipanema
Chico Buarque:Construção" > musicas.txt

# 2. Baixar todas as músicas
uv run harmonic cache --file musicas.txt

# 3. Analisar cada música
uv run harmonic analyze "Djavan" "Sina"
uv run harmonic analyze "Tom Jobim" "Garota de Ipanema"
uv run harmonic analyze "Chico Buarque" "Construção"
```


## Notas
- Use aspas duplas para nomes com espaços
- O cache é útil para análise offline
- Diferentes formatos de saída permitem diferentes usos dos relatórios
- O formato do arquivo de músicas deve ser "artista:musica" (um por linha)

## Tratamento de Erros
O CLI inclui tratamento de erros para situações comuns:

```
# API offline (usará cache se disponível)
uv run harmonic analyze "Djavan" "Sina"

# Música não encontrada
uv run harmonic analyze "Artista Inexistente" "Música Inexistente"
```

## Provider e cache (sem servidor por padrão)

A análise obtém a cifra pela porta `SongProvider`. Por padrão usa o adaptador
**in-process** — raspa o Cifra Club no próprio processo, **sem subir o serviço
Flask**. Flags:

| Flag | Efeito |
| --- | --- |
| `--provider inprocess` | sem servidor (padrão) |
| `--provider http` | usa o serviço Flask em `:3000/api` (`--api-url` p/ outra URL) |
| `--offline` | prioriza o cache local (`CACHE_FIRST`) |
| `--refresh` | força nova busca e reescreve o cache |
| `--no-cache` | desativa o cache |

```bash
# Padrão: in-process, sem subir nada
uv run harmonic analyze "Djavan" "Sina"

# Via serviço HTTP (requer `make scraper` no ar)
uv run harmonic analyze "Djavan" "Sina" --provider http
```
