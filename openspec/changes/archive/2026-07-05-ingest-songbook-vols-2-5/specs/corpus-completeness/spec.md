# corpus-completeness — delta (ingest-songbook-vols-2-5)

## ADDED Requirements

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
