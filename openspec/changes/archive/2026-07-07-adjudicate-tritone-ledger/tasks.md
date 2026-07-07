## 1. Corpus tipado (fundação, sem tocar o build)

- [x] 1.1 Criar `packages/harmonic_analysis/src/harmonic_analysis/corpus/tritone_adjudications.py`: `Citation` (reusar/espelhar `modal_centers.Citation`, `__post_init__` falha-rápido), enum fechado `TritoneVerdictKind` (`subv`/`chromatic_approach`/`emp_legitimate`/`dsec_deceptive`/`ambiguous`), dataclass frozen `TritoneVerdict` (identidade `slug` + `position`, citação obrigatória, `note`), `CORPUS: tuple[...]` (vazio no início), `_INDEX` e `lookup_tritone_verdict(slug, position)`.
- [x] 1.2 Exportar os símbolos novos em `corpus/__init__.py`.
- [x] 1.3 Testes de invariância: veredito sem citação → erro; página/volume inválidos → erro; kind fora do enum → erro; lookup hit/miss; determinismo do `_INDEX`. (gate por importação)

## 2. Auditoria anti-drift (acusa o que falta adjudicar)

- [x] 2.1 Criar `scripts/audit_tritone_adjudication.py` (molde `audit_completeness.py`): re-derivar as ocorrências do ledger com a extração corrente (via `corpus.duckdb`/motor), diff simétrico contra as chaves do corpus — ocorrência sem veredito → falha; veredito órfão → falha; imprime contagem por veredito. Código de saída não-zero em drift.
- [x] 2.2 Rodar a auditoria: ela SHALL listar as 43 ocorrências como pendentes (corpus ainda vazio) — confirma que o anti-drift funciona antes de adjudicar.

## 3. Adjudicação página-a-página (preenche o corpus, cita Chediak)

- [x] 3.1 Extrair a geometria de referência das 43 (centro, raiz→grau, acorde seguinte/alvo) — o join já validado na sonda; salvar como tabela de trabalho no scratchpad para consulta durante a adjudicação.
- [x] 3.2 Adjudicar o cluster **assinatura SubV** (`#11` natural): `samba-de-uma-nota-so` (Ab7#11×6), `aqui-o` (Bb7#11), `beatriz` (A7#11), `ausencia-de-voce` (B7#11) — geometria + citação Chediak (SubV, cap. XXVIII/XXXIV). Preencher vereditos.
- [x] 3.3 Adjudicar o cluster **aproximação cromática descendente**: `minha-namorada` (Eb7→E7), `eh-menina` (Ab7→A7), `demais` (Eb7→E7b9) e afins — citação (SubV/dominante estendido, pág. verificada).
- [x] 3.4 Adjudicar o cluster **empréstimo modal genuíno** (bVI7/bVII7 → repouso): `bye-bye-brasil`, `o-amor-e-chama`, `garota-de-ipanema` (deceptivo) e afins — citação (XXXIV pp.111-116).
- [x] 3.5 Adjudicar o restante caso a caso; marcar `ambiguous` (com nota) o que não fechar com página — incl. os de centro instável (`flora` center=None, etc.). Nunca chutar.
- [x] 3.6 Rodar `audit_tritone_adjudication.py` até **zero pendências** (toda ocorrência adjudicada ou `ambiguous` explícito).

## 4. Cruzamento no ledger + report (aditivo)

- [x] 4.1 Materializar a tabela derivada `tritone_adjudication` no `corpus build` (molde `song_cluster`/`song_neighbor`): a partir do corpus-em-código, chave `(song_id, position)`.
- [x] 4.2 Enriquecer `persistence/views.sql`: `v_ledger_tritone_nondominant` LEFT JOIN → expõe `verdict` + página; ocorrência não-adjudicada → NULL (não some).
- [x] 4.3 Enriquecer `persistence/report.py` / seção do `corpus report`: distribuição por veredito, denominador visível, sem linguagem de placar.

## 5. Verificação ao vivo (invariantes de método)

- [x] 5.1 `uv run python scripts/songbook_baseline.py`: os 3 gates duros SHALL seguir **293/293**; centro/ledger inalterados exceto o cruzamento.
- [x] 5.2 `uv run harmonic corpus gates` e `corpus report`: gates verdes; report mostra a distribuição por veredito.
- [x] 5.3 Teste PRATA: `function_code`/`degree` de toda ocorrência do ledger idênticos pré/pós (o corpus não muta o coder).
- [x] 5.4 `make test` e `make lint` verdes.

## 6. Fecho

- [x] 6.1 Atualizar AGENTS.md/ROADMAP: ledger de trítono adjudicado (contagem por veredito); anotar eventual change de fix downstream sugerida pelos vereditos `subv`/`chromatic_approach`.
- [x] 6.2 `openspec archive adjudicate-tritone-ledger` após validação.
