# CLAUDE.md

Os fatos do projeto (domínio, layout, comandos, fluxo OpenSpec, convenções,
estado) são canônicos em AGENTS.md, importado abaixo:

@AGENTS.md

## Específico do Claude Code

**Modelo por fase:** os skills de spec (`openspec-propose`, `openspec-explore`)
rodam em Opus + `effort: high` via frontmatter; o resto herda o default (Sonnet).
O OpenSpec **regera** esses adaptadores e apaga o `model:/effort:` — após
regenerar, rode `scripts/apply_openspec_models.sh` para reaplicar. Ver a memória
`model-by-phase-strategy`.
