## 1. Corpus tipado (fundação, sem tocar o build)

- [x] 1.1 Criar `packages/harmonic_analysis/src/harmonic_analysis/corpus/tonal_center_adjudications.py`: reusa `Citation` de `modal_centers`; enum fechado `CenterWinner` (`detect`/`functional`/`neither_ii_v`/`modulating`/`ambiguous`); dataclass frozen `TonalCenterVerdict` (`slug`, `curated_root`, `curated_mode` Literal major/minor, `winner`, `evidence`, `citation` opcional só p/ ambiguous); `__post_init__` falha-rápido (citação obrigatória p/ não-ambiguous; ambiguous/modulating exige evidence); `ADJUDICATIONS: tuple[...]` (vazio no início); `_INDEX` + `lookup_center_verdict(slug)`.
- [x] 1.2 Exportar os símbolos novos em `corpus/__init__.py`.
- [x] 1.3 Testes de invariância (molde `test_tritone_adjudications_corpus`): decisivo sem citação → erro; winner fora do enum → erro; ambiguous sem evidência → erro; lookup hit/miss; identidade única por slug.

## 2. Auditoria anti-drift (acusa o que falta adjudicar)

- [ ] 2.1 Criar `scripts/audit_center_adjudication.py` (molde `audit_tritone_adjudication.py`): re-derivar as músicas `center_status='diverge'` do `corpus.duckdb`, diff simétrico contra as chaves do corpus (slug) — diverge sem veredito → falha; veredito órfão → falha; imprime contagem por `winner`. Saída não-zero em drift.
- [ ] 2.2 Rodar a auditoria: SHALL listar as 46 como pendentes (corpus vazio) — confirma o anti-drift antes de adjudicar.

## 3. Adjudicação das 46 (preenche o corpus, cita Chediak)

- [x] 3.1 Extrair a geometria de referência das 46 (detect/funcional/1º/último/âncora V→I) do `worklist_adjudication.py` já rodado; salvar no scratchpad para consulta.
- [x] 3.2 Portar os vereditos da `WORKLIST-ADJUDICATION.md` cuja geometria corrente BATE (eh-menina→detect, ciume/poema-azul/inutil-paisagem/ligia/tereza-da-praia/no-cordao-da-saideira/o-morro-nao-tem-vez/esperanca-perdida/cancao-do-nosso-amor→functional; enquanto-a-tristeza/nos-e-o-mar/imagem/canto-de-ossanha/tema-do-boneco-de-palha/chora-tua-tristeza→detect; bolinha-de-sabao/menina/rio→neither_ii_v; cartao-de-visita→detect; embarcacao/eu-te-amo/ah-se-eu-pudesse/maria-ninguem→modulating). Reexame OBRIGATÓRIO onde o centro funcional deslocou (razao-de-viver funcional D→C).
- [x] 3.3 Adjudicar o cluster **paralela** (12: atras-da-porta, canto-de-ossanha, entrudo, eu-vim-da-bahia, feitinha-pro-poeta, imagem, no-cordao-da-saideira, nos-e-o-mar, o-morro-nao-tem-vez, ponteio, tema-de-amor-por-gabriela, tudo-se-transformou) — modo pela evidência de repouso (maior vs. menor no 1º/último); `ambiguous` se a cadência não fecha o modo. Citar pp.84-85.
- [x] 3.4 Adjudicar os novos **2ªM** (bye-bye-brasil, desafinado, e-luxo-so, menino-das-laranjas, por-causa-de-voce) e **outra** (bloco-do-eu-sozinho, cancao-que-morre-no-ar, samba-da-pergunta, eu-e-a-brisa, tempo-de-solidao) pela cadência visível (âncora V→I ao funcional vs. moldura de abertura do detect).
- [x] 3.5 Adjudicar os **IV↔I** e **V↔I** restantes (amor-em-paz, a-mulher-de-cada-porto, me-perdoe-maria) — distinguir V-como-tônica (detect errou) de armadilha ii-V; marcar `ambiguous`/`modulating` o que não fechar com página. Nunca chutar.
- [x] 3.6 Rodar `audit_center_adjudication.py` até **zero pendências**.

## 4. Cruzamento (view + report, aditivo)

- [x] 4.1 Tabela derivada `center_adjudication` no `schema.sql` + população no `build_corpus` (chave slug→song_id do run).
- [x] 4.2 Nova view `v_center_worklist` em `views.sql` (músicas `diverge` + detect/funcional + LEFT JOIN veredito/página).
- [x] 4.3 Seção no `persistence/report.py`: distribuição por `winner`, denominador visível, sem placar.

## 5. Verificação ao vivo (invariantes de método)

- [x] 5.1 `uv run python scripts/songbook_baseline.py`: 3 gates duros **293/293**; centro 216/262 inalterado (corpus não muta detecção).
- [x] 5.2 `harmonic corpus build` + `corpus gates` + `corpus report`: gates verdes; report mostra a distribuição por `winner`; `v_center_worklist` populada.
- [x] 5.3 Teste PRATA: `center_status`/`center_pc` de toda música idênticos pré/pós.
- [x] 5.4 `make test` e `make lint` verdes.

## 6. Fecho

- [x] 6.1 Atualizar AGENTS.md/ROADMAP: worklist de centro adjudicada (contagem por `winner`); anotar eventual change de fix downstream (armadilha ii-V / V-como-tônica).
- [x] 6.2 `openspec archive adjudicate-center-worklist` após validação (com sync das specs).
