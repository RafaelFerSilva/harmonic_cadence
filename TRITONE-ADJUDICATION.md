# Adjudicação Chediak — ledger de trítono não-dominante (n=532)

**Data:** 2026-07-02 · **Autoridade:** Almir Chediak, *Harmonia & Improvisação* Vol. I,
**cap. XXXIV — "Acordes de sétima da dominante sem função dominante" (pp.111-116)** ·
**Dado:** `v_ledger_tritone_nondominant` (pós-isenção I7, pós `fix-glued-chord-density`,
run corrente n=170; 123/532 ocorrências vêm de cifra parcial — ver quarentena de completude).

> Método: cada padrão foi medido pela **geometria real** (intervalo raiz→tônica detectada,
> e a resolução seguinte), não pelo rótulo do coder. Página citada para cada veredito.
> Chediak p.111: *"os acordes de sétima da dominante, sem função dominante, são
> classificados: função especial não dominante; resolvidos deceptivamente; diatônicos
> cromaticamente alterados."* A síntese da p.115(4): **I7, II7, bVI7, bVII7 e VII7 são
> dominantes de função especial quando têm como resolução esperada o I grau.**

## Vereditos por padrão (raiz real vs. tônica)

| Grau real | Coder diz | n | Veredito | Chediak |
|---|---|---|---|---|
| **bVII7** | `Emp` | 157 | **CONDICIONAL** (ver abaixo) | pp.112(1), 113-114 |
| **VI7** | `T` | 94 | **BUG — T-por-grau** | p.114(1) |
| **bVI7** | `Emp` | 63 | **LEGÍTIMO** (Subd. menor alterada) | quadro p.113, p.113(4) |
| **III7** | `T` | 45 | **BUG — T-por-grau** | p.114(1) |
| **VII7** | `Outro` | 40 | **CLASSIFICÁVEL** (Cadencial especial ou V7/III) | p.112(2), p.115(4) |
| **bIII7** | `T` | 38 | **BUG** (nuance: tom menor/relativa) | p.114 |
| **II7** | `Outro` | 33 | **CLASSIFICÁVEL** (Subd. alterada) | p.113(4), quadro p.113 |
| **bIII7** | `Emp` | 25 | **AMBÍGUO** — mantém no ledger | p.114 |
| **bV7** | `Emp` | 20 | **AMBÍGUO** (possível SubV não detectado) | p.88(c) |
| resíduo | `Emp`/`Crom` | 17 | mantém no ledger | — |

### 1. `Emp` em **bVII7** (157) — o veredito é CONDICIONAL à resolução

Chediak p.112(1): o bVII7 é *"acorde de empréstimo modal (AEM)"* na tonalidade maior
(função **Subd. menor**, quadro p.113), com *"resolução feita por movimento do baixo um tom
acima"* (→I); *"algumas vezes substitui o IVm"*. **Mas** o exemplo da p.114 mostra o MESMO
acorde como **V7/bIII** (dominante secundário do bIII emprestado: `Bb7→Eb7M` em Dó).

Distribuição medida da resolução dos nossos 157: `→bIII` **40** · `→III` 32 · `→I` **31** ·
`→bVII` 25 (repetição) · `→VII` 8 · outros.

- `bVII7→I` (31): **AEM legítimo** — o código `Emp` está CERTO (backdoor, p.112(1)).
- `bVII7→bIII` (40): é **V7/bIII** — dominante secundário; codar `Emp` é **defeito** (o
  correto é `Dsec`, p.114).
- Demais resoluções: caso a caso (deceptivas, p.113(b)).

**Ação:** o coder deve testar a resolução ANTES de rotular: alvo a 4ªJ acima ⇒ `Dsec`;
alvo um tom acima (I) ⇒ `Emp`/AEM citável. Sem regra cega por grau.

### 2. `T` em **VI7 / III7 / bIII7** (177) — bug confirmado: T-por-grau

Em Dó: `A7` (VI7) é **V7/II** e `E7` (III7) é **V7/VI** — dominantes secundários, resolvidos
ou **deceptivos** (p.114(1): *"quando [a resolução diatônica] não acontece trata-se de uma
resolução deceptiva"*, notada `(V7/x)` — a análise permanece de DOMINANTE). O coder atribui
`T` porque a tabela grau→função (I/III/VI→T, p.96) ignora a QUALIDADE: um acorde com trítono
real **nunca** é tônica por posição (única exceção: I7 blues, p.112(3) — já isentada e agora
citável). O `bIII7` com `T` tem nuance (relativa maior em tom menor), mas quality dominante
exclui `T` igualmente.

**Ação:** veto de qualidade no coder — trítono real em grau VI/III/bIII não recebe `T`;
recebe `Dsec` (resolvido ou deceptivo, p.114). É a mesma família do `fix-d2-over-attribution`
(qualidade ≠ função).

### 3. `Outro` em **VII7 / II7** (73) — lacuna classificável

- **VII7** (p.112(2)): função especial **"Cadencial"** quando *"resolvido diretamente no I
  grau… duração longa e não precedido pelo II cadencial"*; senão é **V7/III** (curta duração
  ou cliché `IIm–V7`). Quadro p.113: escala lídio b7/mixolídio.
- **II7** (p.113(4)): relaciona-se com bVI7 pelo mesmo trítono; resolve no I ou I/5ª;
  função **"Subd. alterada"** (quadro p.113). Também pode ser percebido como `#IVm7(b5)`
  de passagem.

**Ação:** novos ramos de classificação com guarda de resolução no I — tira 73 ocorrências do
`Outro` com página citada.

### 4. Isenção I7 — agora com citação completa

A isenção I7-como-tônica (`fix-baseline-noop-gates`) ganha a página: **p.112(3)** — *"o I7 e
IV7 são considerados acordes blues diatônicos (função blues)"*; quadro p.113: I7 = Blues,
escala blues/mixolídio. O **IV7 blues** é a mesma família (hoje o coder o trata via
blues-pos; conferir cobertura na change de fix).

## Consequência para o ledger

Se as ações 1-3 forem implementadas: ~**63** viram `Emp` citável (bVI7) + ~31 `Emp` backdoor
citável + ~40 migram para `Dsec` (V7/bIII) + ~177 deixam de ser `T` (viram `Dsec`) + ~73 saem
de `Outro` (Cadencial/Subd.alt.) → o ledger residual cai para ~**60-90** ambíguos honestos
(bIII7/bV7/resíduos), pesados pela quarentena de completude (123/532 são de cifra parcial).

## Follow-ups recomendados (OpenSpec)

1. **`fix-tritone-t-by-degree`** — ✅ **EXECUTADO** (2026-07-02): ramo 0f, VI7/III7/bIII7 →
   `Dsec` deceptivo (p.114(1)). Ledger 532→318.
2. **`classify-special-function-dominants`** — ✅ **EXECUTADO** (2026-07-02): resolução
   precede empréstimo (bVII7→4ªJ diatônica = `Dsec`, p.114); II7 → `SD` "Subdominante
   alterada" (quadro p.113); VII7 sem tônica → `Dsec (V7/III)` (p.112(2)); isenções
   citáveis no ledger (I7/IV7 blues, bVII7/bVI7 Emp por raiz 10/8, II7 SD). Ledger 318→**20**.
3. ✅ Isenções do baseline + view citando p.112-113 — feito na change 2.

## Estado FINAL da adjudicação (2026-07-02)

Trajetória do ledger: 944 (vacuoso) → 519 (isenção I7) → 532 (pós `fix-glued-chord-density`
recuperar linhas) → 318 (pós follow-up 1) → **20 ocorrências em 10/170 músicas** (pós
follow-up 2). O residual é a classe **bV7 lida como Emp genérico** — ambígua (SubV7/IV não
resolvido? blues #IV? sem página que decida) e honestamente mantida como worklist. Os 3
gates duros permanecem **170/170** e a corroboração de centro inalterada (125/153, 82%)
durante toda a adjudicação. **O capítulo XXXIV do Chediak está integralmente implementado
e citado no coder.**
