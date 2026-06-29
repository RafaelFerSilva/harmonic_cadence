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

## Regra de ouro — separação de responsabilidades (fonte vs. verdade)

- **Cifra Club = input bruto (texto).** É a mina de acordes (sequências de
  caracteres). Sua utilidade **termina no scraping**. As anotações da fonte (o "tom",
  o rótulo maior/menor) são pistas crowdsource-ingênuas, **não a verdade** — confundem
  relativa/paralela, transpõem por tessitura, e **não codificam o centro modal** (provado
  ao vivo: em Arrastão o centro de Chediak é Lá, mas as cifras do CC não têm finalis em Lá).
- **Seu algoritmo + Chediak = ground truth.** O *significado* dos acordes — tensão/repouso,
  centro tonal, nomenclatura modal — só nasce **depois** que o motor (parsers, filtros,
  gates de qualidade) processa o dado bruto, ou quando validado contra a literatura
  (Chediak / academia). Nunca leia o significado direto da anotação da fonte.

Corolário operacional: um alvo de detecção/centro só é implementável se **o dado bruto
o codifica**. Quando o corpus do CC não codifica o fato de Chediak (centro modal), a frente
fica **bloqueada por dado** — precisa de um corpus curado, não de mais mecanismo.

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

Teoria destilada/implementada/testada (38 changes arquivadas + `modal-center-arbitration`
bloqueada, **349 testes verdes**). Corpus de
validação **n=60** (ouro = tom do Cifra Club). Baseline atual: **modo 86% · tônica exata
74% · relativa 81% · coleção 97% · centro estrutural 95% (18/19)** (ver [ROADMAP.md](ROADMAP.md)).

A Fase B (centro tonal) está madura: desempate cadencial (v1, confusão relativa), correção
de modo paralelo (v2), filtro de afinação (v3), e o **gate de qualidade do 3b** — corrige
o V detectado como tônica quando o palpite do K-S aparece só como dominante-7 e resolve num
acorde de repouso (Chediak: tônica repousa, V é tensão; densidade de secundários da MPB
derrota discriminadores estatísticos — só o funcional vence). O modalismo virou **overlay
descritivo** (`modal-coloring`), não eixo concorrente; a detecção de modo automática falsa
foi removida.

**Já fechados (camada de função + detecção):** `dim7-as-dominant` (viio7 = V7(b9) rootless,
Chediak p.90), `loosen-tritone-gate` (V-como-tônica residual: exata 69→74, centro 79→95;
resta só Aquele Abraço = tônica `I7` de funk), `classify-diminished-chords` (diminuto
descendente/auxiliar deixam de ser `Emp`, Chediak pp.102-104). `modal-center-arbitration`
está **bloqueado por dado** (as cifras do CC não codificam o centro modal de Chediak).

Também fechados: `dominant-auxiliary-and-secondary-subv` (Chediak XVIII p.99 — dominante
auxiliar = alvo de empréstimo modal; SubV7 secundário; código `Daux`),
`ii-cadential-secondary-auxiliary` (Chediak XIX p.100 — II cadencial primário/secundário/
auxiliar pelo alvo do dominante; revive o `D2`), `extended-dominants` (Chediak XXVIII(a)
pp.107-108 — dominante que resolve em OUTRO dominante por 4ªJ = `Dext`, sem número romano,
escala mixolídio; gate após o blues) e `extended-subv` (Chediak XXVIII c/d — SubV estendido por
semitom, com **detecção de cadeia** via pré-passe `subv_extended_indices`: runs maximais ≥3,
só a cadeia conta — o par local é ambíguo com blues; corrige o gap `Dext`→`"D"` no macro do
HMM). A preparação de graus (XVIII-XIX) e os dominantes/SubV estendidos (XXVIII a/c/d) estão
completos.

**Frentes abertas:** buracos funcionais do Chediak ainda não cobertos — **acordes
interpolados** (XXIX); e o caso `I7`-funk (Aquele Abraço, único buraco de centro 18/19). **Regra
de ouro:** toda recalibração de detecção mede contra o baseline ao vivo — zero regressão das
corretas é inegociável (já barrou ships ruins).

---

## Pontes por ferramenta (como cada uma lê este arquivo)

- **Claude Code** → `CLAUDE.md` faz `@AGENTS.md` (import nativo).
- **Antigravity** → `.agent/rules/project.md` (`trigger: always_on`) repete as leis
  e aponta para cá; o Antigravity não lê AGENTS.md direto.
- **Gemini CLI** → `~/.gemini/settings.json` com `context.fileName` incluindo
  `AGENTS.md`.
