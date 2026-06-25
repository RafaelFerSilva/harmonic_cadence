# Harmonic Cadence CLI

Interface de linha de comando para análise harmônica de músicas brasileiras.

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/harmonic-cadence.git
cd harmonic-cadence

# Instale usando Poetry
poetry install
```

# Comandos disponíveis no Harmonic CLI

## 1 - analyze - Análise harmônica de músicas

Realiza análise harmônica de uma música específica ou de todas as músicas de um artista.

Sintaxe básica:

    poetry run harmonic analyze ARTISTA [MÚSICA] [OPÇÕES]
Opções:

--all: Analisa todas as músicas do artista (não especifique o nome da música quando usar esta opção)

--format ou -f: Formato do relatório (valores aceitos: html, json, markdown - padrão: json)

Exemplos:
```
# Analisar uma música específica
poetry run harmonic analyze "Djavan" "Flor de Lis" --format html

# Analisar todas as músicas de um artista
poetry run harmonic analyze "Djavan" --all --format markdown
```


## 2. cache - Gerenciamento de cache
Baixa e armazena músicas localmente para uso offline.

Sintaxe básica:

    poetry run harmonic cache [OPÇÕES]

Opções:

--songs: Lista de músicas no formato artista:música (pode especificar múltiplas)

--file ou -f: Arquivo contendo lista de músicas (uma por linha, formato: artista:música)

--artist ou -a: Nome do artista para baixar todas as músicas

--force: Força o download mesmo se a música já existir no cache

Exemplos:

```
# Baixar músicas específicas
poetry run harmonic cache --songs "Djavan:Flor de Lis" "Djavan:Azul"

# Baixar todas as músicas de um artista
poetry run harmonic cache --artist "Djavan"

# Baixar músicas de um arquivo
poetry run harmonic cache --file musicas.txt
```

## 3. list - Listagem de músicas
Lista as músicas disponíveis de um artista, podendo mostrar apenas as em cache.

Sintaxe básica:

    poetry run harmonic list ARTISTA [--cached] [--all]
Opções:

--cached: Lista apenas músicas disponíveis no cache local

Exemplos:
```
# Listar todas as músicas do artista (online)
poetry run harmonic list "Djavan"

# Listar apenas músicas em cache
poetry run harmonic list "Djavan" --cached
```

### Observações importantes:
O comando analyze requer ou um nome de música específico ou a flag --all para analisar todas as músicas.

No comando cache, você pode usar múltiplas formas de especificar as músicas (arquivo, lista direta ou por artista).

O formato padrão para relatórios é JSON, mas você pode escolher entre HTML ou Markdown.

## Outros exemplos

### Análise básica (formato JSON padrão)
    poetry run harmonic analyze "Djavan" "Sina"

### Especificando formato HTML explicitamente
    poetry run harmonic analyze "Djavan" "Sina" --format html

### Análise com saída em Markdown
    poetry run harmonic analyze "Chico Buarque" "Construção" --format markdown

### Para analisar todas as músicas:
    poetry run harmonic analyze "Djavan" --all --format json

### Para analisar uma música específica:
    poetry run harmonic analyze "Djavan" "Flor de Lis" --format html

### Se esquecer de especificar:
    poetry run harmonic analyze "Djavan"


Exemplos com Diferentes Artistas

```
# João Gilberto
poetry run harmonic analyze "Joao Gilberto" "Chega de Saudade"

# Caetano Veloso
poetry run harmonic analyze "Caetano Veloso" "Sampa"

# Tom Jobim
poetry run harmonic analyze "Tom Jobim" "Garota de Ipanema"

# Chico Buarque
poetry run harmonic analyze "Chico Buarque" "Construção"
```

## Cache de Músicas
O CLI permite baixar e cachear músicas para uso offline.

### Cachear uma única música
    poetry run harmonic cache --songs "Djavan:Sina"

### Cachear múltiplas músicas
    poetry run harmonic cache --songs "Djavan:Sina" "Tom Jobim:Garota de Ipanema" "Chico Buarque:Construção"

### Forçar atualização do cache
    poetry run harmonic cache --songs "Djavan:Sina" --force

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

    poetry run harmonic cache --file musicas.txt


# Listar músicas de um artista
    poetry run harmonic list "zeca pagodinho" --all

# Listar apenas músicas em cache
    poetry run harmonic list "zeca pagodinho" --cached

# Baixar todas as músicas de um artista
    poetry run harmonic cache --artist "zeca pagodinho"

# Forçar download de todas as músicas (mesmo que já existam em cache)
    poetry run harmonic cache --artist "zeca pagodinho" --force

## Ajuda

```
# Ver todos os comandos disponíveis
poetry run harmonic --help

# Ajuda específica do comando analyze
poetry run harmonic analyze --help

# Ajuda específica do comando cache
poetry run harmonic cache --help
```



## Exemplos de Workflow
### Workflow Básico

```
# 1. Baixar música para cache
poetry run harmonic cache --songs "Djavan:Sina"

# 2. Analisar a música
poetry run harmonic analyze "Djavan" "Sina"
```

## Workflow com Múltiplas Músicas
```
# 1. Criar arquivo de músicas
echo "Djavan:Sina
Tom Jobim:Garota de Ipanema
Chico Buarque:Construção" > musicas.txt

# 2. Baixar todas as músicas
poetry run harmonic cache --file musicas.txt

# 3. Analisar cada música
poetry run harmonic analyze "Djavan" "Sina"
poetry run harmonic analyze "Tom Jobim" "Garota de Ipanema"
poetry run harmonic analyze "Chico Buarque" "Construção"
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
poetry run harmonic analyze "Djavan" "Sina"

# Música não encontrada
poetry run harmonic analyze "Artista Inexistente" "Música Inexistente"
```
