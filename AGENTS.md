# AGENTS.md

> Fonte canônica de fatos do projeto para qualquer ferramenta de AI
> (Claude Code, Antigravity, Gemini CLI). Cada ferramenta lê isto por um caminho
> próprio — ver "Pontes por ferramenta" no fim.

Análise harmônica automática de MPB: a partir de cifras do Cifra Club, extrai
acordes, tonalidade, graus, funções, cadências e progressões, e gera relatórios
(JSON/Markdown/HTML). Monorepo `uv` com núcleo compartilhado + CLI + scraper.

## Regra inegociável — Chediak é o árbitro teórico

Toda decisão harmônica deve ser checada contra **Almir Chediak, _Harmonia &
Improvisação_ Vol. I** (a autoridade do projeto): **cite a página**, registre
divergências, **nunca chute**. Quando a teoria for ambígua, o livro decide. Modelo
interno em inglês canônico (`Note` soletrada, bemóis corretos — `Bb`, não `A#`);
relatórios humanos em PT-BR.

## Layout (monorepo `uv` workspace)

```
packages/
├── cifra_core/         # núcleo: encoding, filtro de linhas (idempotente),
│                       #   regex de acorde, Cifra/SongRef, SongProvider, cache
├── cifra_scraper/      # API Flask (BeautifulSoup) em :3000/api — serviço opcional
└── harmonic_analysis/  # domínio musical + CLI `harmonic` + relatórios
```

A análise obtém cifras **só** pela porta `SongProvider`. Dois adaptadores:
**in-process** (padrão, raspa sem subir servidor) e **HTTP** (fala com o Flask).
Cache via `CachePolicy` (`NETWORK_FIRST`/`CACHE_FIRST`/`CACHE_ONLY`/`REFRESH`).

## Comandos

```bash
uv sync                                  # instala todo o workspace
uv run harmonic analyze "Djavan" "Sina"  # CLI (in-process, sem servidor)
make test                                # uv run pytest (toda a suíte)
make lint                                # uv run ruff check packages
uv run python scripts/key_baseline.py    # baseline de tonalidade (precisa de rede)
make scraper                             # sobe o Flask em :3000 (só p/ --provider http)
```

- Python ≥ 3.12, `ruff` line-length 88, `pytest` testpaths = `packages`.
- Testes ficam em `packages/<pkg>/tests`; layout `src/` em cada pacote.

## Fluxo de trabalho — OpenSpec (obrigatório p/ mudanças não-triviais)

Cada melhoria é uma **change OpenSpec**: proposal → design → specs → tasks →
implementar → `openspec archive`. O OpenSpec é a **espinha agnóstica de
ferramenta**: a verdade vive em `openspec/specs/` (capabilities) e
`openspec/changes/` (arquivadas em `openspec/changes/archive/AAAA-MM-DD-<nome>/`).

```bash
openspec list           # changes ativas
openspec list --specs   # capabilities (specs)
```

## Convenções

- **Git:** branch dedicada para mudanças grandes — `feature/<slug>` ou `fix/<slug>`.
- **Uma fonte de nota** (`Note` soletrada) e **uma detecção de tom** (`detect_key`)
  em todos os entry points — não reintroduzir subsistemas paralelos.
- Seções de análise degradam **visíveis** (`_safe_section` + `result["diagnostics"]`),
  nunca em silêncio.

## Estado atual

Teoria destilada/implementada/testada (~26 changes, **300 testes verdes**). Corpus de
validação **n=60** (ouro = tom do Cifra Club). Baseline atual: **modo 86% · tônica exata
69% · relativa 76% · coleção 97% · centro estrutural 79%** (ver [ROADMAP.md](ROADMAP.md)).

A Fase B (centro tonal) está madura: desempate cadencial (v1, confusão relativa), correção
de modo paralelo (v2), filtro de afinação (v3), e o **gate de qualidade do 3b** — corrige
o V detectado como tônica quando o palpite do K-S aparece só como dominante-7 e resolve num
acorde de repouso (Chediak: tônica repousa, V é tensão; densidade de secundários da MPB
derrota discriminadores estatísticos — só o funcional vence). O modalismo virou **overlay
descritivo** (`modal-coloring`), não eixo concorrente; a detecção de modo automática falsa
foi removida.

**Próxima frente:** `modal-center-arbitration` (Arrastão→Lá: ausência de dominante + cadência
modal → finalis; + métrica de centro modal degree-relative). Depois: afrouxar o gate p/ os 4
V-como-tônica restantes (guiado por dado, com a trava do baseline); e dim7-como-dominante
(viio7 = V7b9). **Regra de ouro:** toda recalibração de detecção mede contra o baseline ao
vivo — zero regressão das corretas é inegociável (já barrou 2 ships ruins).

---

## Pontes por ferramenta (como cada uma lê este arquivo)

- **Claude Code** → `CLAUDE.md` faz `@AGENTS.md` (import nativo).
- **Antigravity** → `.agent/rules/project.md` (`trigger: always_on`) repete as leis
  e aponta para cá; o Antigravity não lê AGENTS.md direto.
- **Gemini CLI** → `~/.gemini/settings.json` com `context.fileName` incluindo
  `AGENTS.md`.
