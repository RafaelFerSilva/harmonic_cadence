# Harmonia - Análise Harmônica de Músicas

Projeto para análise harmônica automática de músicas brasileiras, com extração de acordes, graus, funções harmônicas e cadências.

## Estrutura

- `domain/` - Lógica de negócio (acordes, funções, cadências)
- `infra/` - Infraestrutura (API, scraping)
- `services/` - Orquestração e casos de uso
- `cli/` - Interface de linha de comando
- `tests/` - Testes automatizados

## Como rodar

1. Instale as dependências:

    ```
    pip install -r requirements.txt
    ```

2. Execute a interface CLI:
    ```
    python -m cli.main
    ```
## Como contribuir

- Siga a estrutura de diretórios
- Escreva testes para novas funções
- Documente suas funções e módulos

---

Projeto em desenvolvimento. Sinta-se à vontade para sugerir melhorias!
