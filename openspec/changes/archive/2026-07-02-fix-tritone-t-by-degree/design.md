## Context

`HarmonicAnalysis.analyze_function` (harmony.py) tem uma cascata para dominante-7 (ramos
0a-0e: blues I7/IV7, Dext, SubV secundário, Daux, Emp bVII7/bVI7, Dsec por resolução, VII7
cadencial, bII7 SubV). Um dominante-7 que não casa NADA atravessa o bloco e cai na leitura
diatônica por grau (I/III/VI→T, p.96) — dando `T` a `A7`/`E7` em Dó. A adjudicação
(`TRITONE-ADJUDICATION.md`) mediu 177 casos e citou o veredito: Chediak p.114(1), secundário
**deceptivo** — análise permanece de dominante.

## Goals / Non-Goals

**Goals:**
- Ramo 0f: fall-through de dominante-7 em VI/III/bIII → `Dsec` deceptivo `(V7/x)`.
- Ledger cai ~177; `T` deixa de conter trítono real fora do I7 blues.
- Gates duros seguem 170/170 (re-medição ao vivo).

**Non-Goals:**
- `II7`/`VII7` função especial (p.115(4)) e `bV7` — change `classify-special-function-dominants`.
- `bVII7` condicional (V7/bIII vs. AEM) — idem.
- Nenhuma mudança em detecção de tom, cadência, HMM (consomem a saída).

## Decisions

### D1 — Ramo 0f no FIM da cascata, escopo = posições {9, 4, 3}
Só dispara após 0a-0e falharem (zero mudança de rótulo nos caminhos existentes) e só para
raiz a 9 (VI), 4 (III) ou 3 (bIII) semitons da tônica — as três posições adjudicadas como
bug. Posições 2 (II7) e 11-sem-resolução (VII7) seguem no fall-through atual (`Outro`),
reservadas para a próxima change com o rótulo Chediak correto (Cadencial/Subd. alterada) —
rotulá-las `Dsec` agora seria trocar um erro por outro (p.115(4) as chama de função
especial, não deceptiva).

### D2 — Código `Dsec`, descrição explicita a decepção
Reusa o código `Dsec` existente (consumidores já o tratam como dominante: gates, HMM macro
D, cadência não-repouso) com nome "Dominante Secundário deceptivo (V7/x)" e descrição
citando p.114. O alvo esperado `x` = grau diatônico a 4ªJ acima da raiz (`(Vroot+5)%12`).
*Alternativa:* novo código `Ddec` — rejeitado (explode a taxonomia de 14 códigos, function_ref,
HMM e views para ganho zero: a macro-função é a mesma).

### D3 — Sem condição de next_chord
O deceptivo é justamente o caso em que a resolução esperada NÃO acontece — exigir next seria
contraditório; último acorde da música também qualifica. Os casos COM resolução funcional já
foram capturados por 0b/0d antes.

## Risks / Trade-offs

- **[Mudar estatísticas de função do corpus]** → esperado (o dado estava errado); re-medição
  e AGENTS atualizados na change.
- **[Um `T` legítimo perdido]** → não existe: trítono real como repouso só tem uma exceção em
  Chediak (I7 blues, 0a, intocado). `bIII7` em tom menor (relativa) segue a mesma lógica —
  qualidade dominante exclui repouso.
- **[Cadências mudam]** → desejado e já protegido: `analyze_cadences` suprime alvo
  não-repouso (gate 4 permanece verde por construção; re-medido mesmo assim).

## Migration Plan

Aditivo no coder; rollback = remover o ramo 0f. Corpus regenerável (`corpus build`).

## Open Questions

- Nenhuma bloqueante.
