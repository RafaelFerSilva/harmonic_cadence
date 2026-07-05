# corpus-completeness Specification

## Purpose
TBD - created by archiving change corpus-completeness-quarantine. Update Purpose after archive.
## Requirements
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

### Requirement: Entradas resolvidas do ledger são aposentadas com proveniência

O sistema SHALL aposentar do ledger curado a entrada de uma música quarentenada quando sua
cifra é **recuperada da fonte** (re-transcrição do songbook original), com **registro da
resolução** (nota de proveniência no módulo do ledger: data e fonte da recuperação). Após a
recuperação, a auditoria local SHALL confirmar a ausência de divergência para o slug (o
vocabulário declarado pela fonte está contido na extração do arquivo novo), e a
materialização SHALL estampar a música como `complete`.

#### Scenario: Cifra re-transcrita sai da quarentena

- **WHEN** uma música `incomplete` é re-transcrita da página do songbook e o vocabulário dos
  diagramas do livro está contido na extração do arquivo novo
- **THEN** sua entrada SHALL ser removida do ledger (com nota de proveniência) e o próximo
  `corpus build` SHALL estampá-la `complete`

#### Scenario: Auditoria confirma a resolução

- **WHEN** `audit_completeness.py` roda após a recuperação
- **THEN** o slug recuperado SHALL NOT aparecer nem como divergência auditada nem como
  entrada de ledger sem suporte

### Requirement: Admissão de cifra nova da fonte primária é verificada por vocabulário
A new chart transcribed from the primary source (a songbook page) SHALL enter the corpus
(`cifras/<slug>.md`) only after a mechanical vocabulary check: the set of chords extracted
from the new file by the canonical extraction path MUST be a superset of the chords the
book page declares in its diagrams (`extração ⊇ diagramas`), with mere spelling differences
normalized to the project's canonical spelling. The `Acordes Utilizados:` header manifest
MUST come from the printed diagrams (the vocabulary the book declares), never from the
extraction itself. An admitted chart enters with completeness `complete` and the
completeness audit MUST NOT flag it. A song whose page does not allow the check (illegible,
diagrams absent) MUST NOT be admitted — it SHALL be reported as a pending item with its
page, never transcribed by guessing.

#### Scenario: Cifra verificada é admitida como complete
- **WHEN** uma música do songbook é transcrita no tom impresso e a extração do arquivo
  novo contém todos os acordes dos diagramas da página (após normalização de grafia)
- **THEN** o arquivo entra no corpus com manifesto derivado dos diagramas, a completude
  estampada é `complete` e `scripts/audit_completeness.py` fecha sem drift para o slug

#### Scenario: Verificação reprovada bloqueia a admissão
- **WHEN** a extração do arquivo transcrito NÃO cobre os diagramas da página (acorde do
  livro ausente do corpo transcrito)
- **THEN** o arquivo NÃO entra no corpus até a transcrição ser corrigida, e a divergência
  é tratada como erro de transcrição (hipótese nº 1), não como defeito do motor

#### Scenario: Página sem oráculo vira pendência, não admissão
- **WHEN** a página da música está ilegível ou sem diagramas utilizáveis
- **THEN** a música fica fora do corpus, listada como pendência com volume e página —
  admissão sem oráculo é proibida

#### Scenario: Colisão de slug nunca sobrescreve
- **WHEN** o slug de uma música nova colide com um `cifras/<slug>.md` existente
- **THEN** o arquivo existente NÃO é sobrescrito; a colisão é investigada e a decisão
  registrada na change

