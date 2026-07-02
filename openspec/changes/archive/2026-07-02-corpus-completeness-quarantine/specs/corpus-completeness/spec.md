## ADDED Requirements

### Requirement: Ledger curado de completude com evidência obrigatória

O sistema SHALL manter um ledger curado e versionado de completude do corpus
(`harmonic_analysis.corpus.completeness`), com um fato tipado por música quarentenada:
`slug`, `status` (`incomplete` = oráculo da fonte confirma ausência; `suspect` = manifesto
independente diverge sem fonte confirmadora), os símbolos de acorde declarados-e-ausentes
(`missing_declared`, não-vazio) e a **evidência obrigatória** (fonte da declaração). A
construção de um fato sem evidência ou sem acordes ausentes SHALL falhar na importação
(`__post_init__`). O ledger SHALL conter apenas fatos (slugs, símbolos, fonte da evidência) —
nunca texto de cifra (fronteira de copyright). Uma música ausente do ledger é `complete` por
default; corpora sem oráculo (ex.: v3, fonte deletada e manifesto derivado do corpo) SHALL NOT
ser quarentenados sem evidência.

#### Scenario: Fato sem evidência falha rápido

- **WHEN** um fato de completude é construído com evidência vazia ou sem acordes ausentes
- **THEN** a construção SHALL lançar erro na importação do módulo (o fato não existe sem
  evidência)

#### Scenario: Ausência de oráculo não vira quarentena

- **WHEN** uma música vem de uma fonte sem vocabulário declarado independente
- **THEN** ela SHALL permanecer `complete` por default — quarentena exige evidência, não
  suspeita gratuita

### Requirement: Auditoria local verifica o ledger contra a evidência re-derivada

O sistema SHALL prover um script de auditoria local que re-deriva a evidência de completude —
comparando o vocabulário declarado (manifesto do arquivo e, quando a fonte v4 estiver
presente, o header `Acordes:` do livro) com os acordes extraídos pelo caminho canônico de
extração corrente — **descontando dialeto** (grafias com os mesmos pitch-classes via parse)
antes de acusar ausência. O script SHALL comparar o resultado com o ledger curado e reportar
divergências nas duas direções (entrada curada sem suporte; divergência sem entrada), sem
alterar o ledger (o curador decide). Sem `cifras/` locais o script SHALL avisar e sair sem
erro (ferramenta local).

#### Scenario: Auditoria acusa drift do ledger

- **WHEN** a extração melhora e um acorde antes ausente passa a ser extraído
- **THEN** a auditoria SHALL reportar a entrada do ledger que perdeu suporte, para
  re-curadoria — e SHALL NOT remover a entrada automaticamente

#### Scenario: Dialeto não vira ausência

- **WHEN** o vocabulário declarado grafa `C9` e o corpo grafa `C7(9)` (mesmos pitch-classes)
- **THEN** a auditoria SHALL NOT contar `C9` como acorde ausente

### Requirement: Completude estampada na persistência e visível no relatório

A materialização do corpus SHALL estampar `song.completeness`
(`complete`/`suspect`/`incomplete`) a partir do ledger curado, por slug. O `corpus report`
SHALL mostrar a contagem por status na seção de corpus e SHALL marcar, na worklist de
curadoria do trítono, os padrões cujos exemplos venham de músicas quarentenadas. Os gates
duros SHALL NOT filtrar por completude — o invariante por ocorrência vale em cifra parcial; a
completude é qualidade do dado de entrada, não veredito sobre a análise.

#### Scenario: Materialização estampa por slug

- **WHEN** `corpus build` materializa uma música cujo slug está no ledger como `incomplete`
- **THEN** a linha de `song` SHALL registrar `completeness='incomplete'`; músicas fora do
  ledger SHALL registrar `complete`

#### Scenario: Report dá visibilidade sem linguagem de defeito

- **WHEN** o relatório é gerado sobre um corpus com músicas quarentenadas
- **THEN** a seção de corpus SHALL mostrar a contagem por status de completude, apresentada
  como qualidade do dado de entrada (nunca como erro do motor)

#### Scenario: Gates não filtram por completude

- **WHEN** `corpus gates` roda sobre um corpus com músicas quarentenadas
- **THEN** as views de gate SHALL continuar avaliando todas as ocorrências, inclusive das
  músicas quarentenadas (um acorde presente obedece Chediak independentemente de a cifra
  estar completa)
