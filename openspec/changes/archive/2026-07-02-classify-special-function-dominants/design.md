## Context

Cascata de dominante-7 em `analyze_function` (pós-0f): 0a blues → 0a' Dext → 0b SubV-sec/Daux
→ **0c Emp bVII7/bVI7** → **0d Dsec-por-resolução/VII7-cadencial** → 0e SubV → 0f deceptivo
VI/III/bIII. O bug de ordem: 0c captura bVII7 ANTES do teste de resolução 4ªJ-diatônica de
0d — em tom menor, `bVII7→bIII` (V7/III real, Chediak p.114 usa exatamente `Bb7→Eb` como
exemplo) vira `Emp`. Em tom maior o alvo 4ªJ do bVII7 é não-diatônico e o `Daux` (0b) já o
captura — o buraco é específico do campo menor.

Ledger atual (318): bVII7≈157 (condicional), bVI7≈63 (legítimo), VII7=40 (`Outro`),
II7=33 (`Outro`), bV7≈20 (ambíguo), resíduos.

## Goals / Non-Goals

**Goals:**
- Resolução precede empréstimo (promessa do comentário do bloco 0 vira código).
- II7 e VII7-não-resolvido classificados com página (p.112(2), p.113).
- Ledger isenta as funções especiais documentadas (quadro p.113) com citação; residual
  honesto ~25-90.

**Non-Goals:**
- bV7 (20) permanece no ledger (ambíguo: SubV7/IV? blues #IV? — sem página que decida).
- Nenhuma mudança em detecção de tom, cadência, HMM, D2.
- Nenhum código novo na taxonomia (reusa `Dsec`/`SD`/`Emp`/`D`).

## Decisions

### D1 — Mover o teste Dsec-por-resolução para ANTES do Emp (0c⇄0d parcial)
Apenas o sub-ramo `ni==5 and not target_is_tonic → Dsec` sobe para antes de 0c. O
`VII7→tônica → D cadencial` permanece onde está (depois de 0c não interfere: pos 11 ∉
{10, 8}). Menor movimento possível; o comentário do bloco já declara essa precedência.

### D2 — II7 → `SD` "Subdominante alterada (II7)" (quadro p.113)
Chediak dá a FUNÇÃO: "Subd. alt." — família subdominante, não dominante nem Outro. Código
`SD` existente com nome/descrição próprios e citação. Posição 2 exata, só no fall-through
(depois de 0e/0f), não colide com Dsec-por-resolução (um `D7→G7M` em Dó é ni==5 → Dsec
V7/V, correto e intocado).

### D3 — VII7 sem resolução no I → `Dsec (V7/III)` (p.112(2))
O livro dá as duas leituras do VII7: Cadencial (→I, já coberto) ou **V7/III** ("duração
curta ou cliché IIm–V7"). Sem informação de duração, o fall-through (não resolveu no I nem
no III — senão 0d/reordenado pegaria) é a expectativa deceptiva `(V7/III)` (p.114). Estende
o 0f para pos 11 com alvo fixo III.

### D4 — Isenção citável no ledger: par (posição, função) documentado no quadro p.113
Baseline e view isentam: I7→`T` (grau I, já existe — p.112(3)); IV7→`SD` (grau IV);
bVII7/bVI7→`Emp`; II7→`SD` (nome "alterada"). Implementação na view: juntar com
`chord_vocab.root_pc` e a tônica não está na view… → mais simples e robusto: isentar por
(função, grau-cru): `T`/I (existe), `SD`/IV, `SD`/II, `Emp`/qualquer (bVII7/bVI7 são as
únicas fontes de Emp dominant-quality no coder pós-mudança — os outros Emp de trítono
migraram p/ Dsec). No baseline, a MESMA regra em Python. Documentar que a isenção de `Emp`
é válida porque o coder só emite Emp p/ dominante-7 nas posições 10/8 (invariante do código,
coberto por teste).

### D5 — Zero mudança de rótulo fora do campo menor + fall-throughs
A reordenação só altera casos onde 0c capturava algo que 0d capturaria (bVII7/bVI7 com
resolução 4ªJ diatônica = só tom menor). Teste dedicado prova: em Dó MAIOR, `Bb7→C` (AEM)
segue `Emp`; em Lá MENOR, `G7→C` (bVII7→bIII) vira `Dsec (V7/III)`.

## Risks / Trade-offs

- **[Isenção Emp ampla demais]** → travada pelo invariante "coder só emite Emp
  dominante-quality em pos 10/8" (teste); se um futuro ramo emitir Emp noutra posição, o
  teste quebra e força revisão da isenção.
- **[Rótulos mudam em tom menor]** → intencional e citado (p.114); baseline ao vivo decide.
- **[VII7 V7/III sem duração]** → aproximação honesta da regra de duração do livro; o caso
  →I (Cadencial) e →III (Dsec normal) já saem antes; só o resto recebe a expectativa.

## Migration Plan

Coder + baseline + view na mesma change (isenções e classificação andam juntas). Corpus
regenerável. Rollback = reverter commit.

## Open Questions

- Nenhuma bloqueante.
