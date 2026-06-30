## Context

O ramo 0e de `analyze_function` ([harmony.py:293-318]) emite `D2` quando o acorde é menor, o
**próximo** é dominante-7 por qualidade, e o intervalo é 4ªJ — sem checar resolução. Probe ao
vivo (n=62): **363 `D2`, 164 com o V NÃO resolvendo** (over-attribution), 199 resolvem.

Duas armadilhas que o design precisa evitar:
1. **Checar o CÓDIGO do V não serve.** O ramo de blues (0a) coda `I7`/`IV7` (pos 0/5) como
   `T`/`SD` **antes** de considerar resolução. Um `Cm7 F7→Bb` legítimo tem `F7` em pos 5 → codado
   `SD` — checar "V tem código dominante" rejeitaria um D2 correto.
2. **A recursão simples (avaliar o V sem o next-next) também não serve** — `analyze_function(F7,
   next=None)` cairia em blues pos-5 → `SD`. Precisa do acorde APÓS o V para saber se resolve.

O teste correto é **a resolução do V**, que é **puramente intervalar** (não precisa do tom nem do
código): o acorde em `i+2` baixa em `alvo = (Vroot+5)%12`? Isso espelha exatamente o pré-passe
`subv_extended_indices` (classmethod intervalar sobre a progressão inteira, threaded como flag).

## Goals / Non-Goals

**Goals:**
- `D2` só quando o V resolve no alvo (164 over-attributions → 0; 199 legítimos preservados).
- Transposição-invariante; fonte única (`analyze_function`); zero regressão dos invariantes.

**Non-Goals:**
- Detecção de tom (a-ra em quarentena — fora de escopo).
- Gatear o invariante ii-V no baseline (change futura, após contagem 0).
- Mexer no ramo de blues (0a) ou em qualquer outro código de função.

## Decisions

**D1 — Pré-passe classmethod `ii_cadential_indices(chords)`, no molde do `subv_extended_indices`.**
Para cada `i` com `chords[i].is_minor`, `chords[i+1].is_dominant_seventh`,
`_get_interval(chords[i].root, chords[i+1].root) == 5`: marca `i` como D2-válido **sse** existe
`chords[i+2]` e (`chords[i+2].root` **ou** `chords[i+2].bass`) `== (chords[i+1].root + 5) % 12`.
Classmethod intervalar (sem `self.key`), igual ao `subv_extended_indices`. *Alternativa
rejeitada:* recursão sem next-next (quebra o auxiliar pos-5, ver Context) e checagem por código
do V (mascarada pelo blues).

**D2 — Ramo 0e ganha um flag `ii_cadential: bool` (5º parâmetro, default False), como o
`subv_extended`.** A condição de emissão do `D2` passa a exigir `ii_cadential` verdadeiro. Os 2
call sites (`analysis_service.py:198`, `formatter.py:80`) computam `ii_idx =
HarmonicAnalysis.ii_cadential_indices(all_chords)` (uma vez) e passam `i in ii_idx` — exatamente
a fiação já usada para `i in subv_members`.

**D3 — V no fim da progressão (sem `i+2`): NÃO é D2.** Sem o acorde de resolução não há evidência
de que o V funcione; conservador. (No corpus atual: 0 casos, então não afeta o gate; é a regra
honesta para o futuro.)

**D4 — Resolução por raiz OU baixo do alvo.** Cobre alvos invertidos (ex.: resolver em `C/E`),
consistente com o critério de baixo já usado no `chediak_functional_center`.

## Risks / Trade-offs

- **[Resolução a um dominante (chain) conta como válida]** ex.: `Em7 A7→D7` — `A7` resolve em `D`
  (raiz), `D7` é dominante. → Mitigação: CORRETO — `A7` funciona como dominante por resolver 5ªJ
  abaixo; `Em7` é um ii-V secundário legítimo (a qualidade do alvo não desqualifica o V). É o
  oposto da guarda de TÔNICA do `harden-functional-center` (lá o alvo-tônica precisa ser repouso;
  aqui só checamos que o V funciona).
- **[Testes do `D2` antigo quebram]** → Mitigação: ajustar os que codificavam D2 sobre um V
  não-resolvente, documentando que o comportamento antigo era a super-atribuição; manter/expandir
  os de D2 legítimo (resolvente).
- **[Acorde que perde D2 vira função "errada"]** → o menor cai na leitura diatônica/outra; como a
  super-atribuição não era um ii cadencial, qualquer leitura ordinária é mais correta. Os
  invariantes do baseline só checam dom-7 e diminuto (não o menor), logo intactos.

## Migration Plan

1. Adicionar `ii_cadential_indices(cls, chords) -> set` em `HarmonicAnalysis` (molde do
   `subv_extended_indices`; teste de resolução por raiz/baixo do alvo).
2. `analyze_function`: novo param `ii_cadential: bool = False`; o ramo 0e só emite `D2` se
   `ii_cadential`.
3. Fiar os 2 call sites: computar `ii_idx` e passar `i in ii_idx` (como `subv_members`).
4. Testes unitários do ramo (resolve→D2; não-resolve→não-D2; fim-de-progressão→não-D2;
   `Em7 A7→D7` secundário→D2; `Cm7 F7→Bb` auxiliar→D2).
5. **Gate ao vivo:** re-rodar o probe de `D2` — não-resolventes 164→0, resolventes 199 mantidos;
   `songbook_baseline.py` trítono/diminuto 62/62; `make test`/`make lint`.

## Open Questions

- Nenhuma bloqueante. (Gatear o invariante "todo `D2` resolve" no `songbook_baseline.py` é
  natural após esta fix, mas fica para a change que fecha o #6.)
