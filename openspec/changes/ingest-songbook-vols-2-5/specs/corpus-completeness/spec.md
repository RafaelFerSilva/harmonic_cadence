# corpus-completeness — delta (ingest-songbook-vols-2-5)

## ADDED Requirements

### Requirement: Admissão de cifra nova da fonte primária é verificada por vocabulário
Uma cifra nova transcrita da fonte primária (página do songbook) SÓ entra no corpus
(`cifras/<slug>.md`) após verificação mecânica de vocabulário: o conjunto de acordes
extraído do arquivo novo pelo caminho canônico de extração DEVE ser superconjunto dos
acordes que a página do livro declara nos diagramas (`extração ⊇ diagramas`), com
diferenças de mera grafia normalizadas para a grafia canônica do projeto. O manifesto
`Acordes Utilizados:` do header DEVE vir dos diagramas impressos (o vocabulário que o
livro declara), nunca da própria extração. A cifra admitida entra com completude
`complete` e a auditoria de completude NÃO a acusa. Uma música cuja página não permita a
verificação (ilegível, diagramas ausentes) NÃO é admitida — ela DEVE ser reportada como
pendência com a página, nunca transcrita por palpite.

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
