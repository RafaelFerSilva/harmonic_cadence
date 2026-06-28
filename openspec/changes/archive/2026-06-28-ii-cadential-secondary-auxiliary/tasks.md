## 1. Trava (antes de tocar código)

- [x] 1.1 `make test` — registrar a contagem verde (referência).
- [x] 1.2 Sondagem (já feita): `Dm7 G7→C`→SD; `F#m7 B7→Em`→Emp; `Am7 D7→G`→T; `Cm7 F7→Bb`→T; `Bbm7 Eb7→Ab`→Emp.

## 2. Ramo de II cadencial (harmony.py)

- [x] 2.1 Inserir, ANTES da seção 1 (diatônica), um ramo: `chord.is_minor` e `next_chord.is_dominant_seventh` e `_get_interval(chord.root, next_chord.root) == 5` (ii→V, 4ªJ asc).
- [x] 2.2 Computar `alvo_pc = (Note.parse(next_chord.root).pitch_class + 5) % 12` e `alvo_off = (alvo_pc - key_pc) % 12`. Classificar: `alvo_pc==key_pc`→primário; `alvo_pc in scale_pcs`→secundário; senão→auxiliar.
- [x] 2.3 Retornar código `D2` com nome "II cadencial {tipo} (de V7/{grau})" usando `_CHROMATIC_DEGREE[alvo_off]`; descrição cita Chediak p.100.
- [x] 2.4 Remover o ramo `D2` morto da seção 2 (substituído por este, que é alcançável).

## 3. Testes

- [x] 3.1 Primário: `Dm7 G7` (alvo C) → `D2` "primário".
- [x] 3.2 Secundário: `F#m7 B7` (alvo E=III) → `D2` "secundário (de V7/III)"; `Am7 D7` (alvo G=V) → "secundário (de V7/V)".
- [x] 3.3 Auxiliar: `Cm7 F7` (alvo Bb=bVII) → `D2` "auxiliar (de V7/bVII)"; `Bbm7 Eb7` (alvo Ab=bVI) → "auxiliar (de V7/bVI)".
- [x] 3.4 Guard: acorde menor NÃO seguido de dominante 4ªJ acima (ex.: `Dm7 C`) → não é II cadencial (segue função normal).
- [x] 3.5 Ajustar/atualizar qualquer teste que codificava `Dm7→G7 = SD` para o novo `D2` (rótulo fiel).

## 4. Quality gate + docs

- [x] 4.1 `make test` verde; `make lint` limpo.
- [x] 4.2 `scripts/key_baseline.py` ao vivo: baseline **idêntico** (não toca `detect_key`).
- [x] 4.3 Atualizar `ROADMAP.md` (II cadencial secundário/auxiliar, Chediak XIX p.100; fecha a frente XVIII-XIX).
- [x] 4.4 `openspec validate ii-cadential-secondary-auxiliary --strict` passa; pronto para `openspec archive`.
