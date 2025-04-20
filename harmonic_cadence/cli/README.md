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

## Uso
Análise de Músicas
Você pode analisar músicas usando diferentes formatos de saída (HTML, PDF, Markdown).


### Análise básica (formato JSON padrão)
    poetry run harmonic analyze "Djavan" "Sina"

### Especificando formato HTML explicitamente
    poetry run harmonic analyze "Djavan" "Sina" --format html

### Análise com saída em Markdown
    poetry run harmonic analyze "Chico Buarque" "Construção" --format markdown


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
poetry run harmonic list "zeca pagodinho"

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

## Formatos de Saída
- JSON: Formato padrão para integração com sistemas
- HTML: Relatório interativo para visualização em navegador
- Markdown: Formato texto simples para documentação ou GitHub

## Tratamento de Erros
O CLI inclui tratamento de erros para situações comuns:

```
# API offline (usará cache se disponível)
poetry run harmonic analyze "Djavan" "Sina"

# Música não encontrada
poetry run harmonic analyze "Artista Inexistente" "Música Inexistente"
```
