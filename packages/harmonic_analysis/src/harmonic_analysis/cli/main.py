import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

from tqdm import tqdm

from cifra_core import CachePolicy, cifra_from_text

from harmonic_analysis.config import ProviderConfig, build_song_provider
from harmonic_analysis.infra.cifra_api import (
    cache_all_artist_songs,
    download_and_cache_song,
    fetch_artist_songs,
    load_artist_songs,
)
from harmonic_analysis.presentation.reports.factory import ReportFactory
from harmonic_analysis.services.analysis_service import AnalysisService


class HarmonicCLI:
    """Interface de linha de comando para o Harmonic Cadence."""

    def __init__(self):
        self.parser = self._create_parser()

    def _build_service(self, args: argparse.Namespace) -> AnalysisService:
        """Raiz de composição: monta o SongProvider a partir das flags."""
        policy = CachePolicy.NETWORK_FIRST
        if getattr(args, "offline", False):
            policy = CachePolicy.CACHE_FIRST
        if getattr(args, "refresh", False):
            policy = CachePolicy.REFRESH

        kwargs: dict = {
            "kind": getattr(args, "provider", "inprocess"),
            "cache_enabled": not getattr(args, "no_cache", False),
            "cache_policy": policy,
        }
        if getattr(args, "api_url", None):
            kwargs["api_base_url"] = args.api_url
        return AnalysisService(build_song_provider(ProviderConfig(**kwargs)))

    def _create_parser(self) -> argparse.ArgumentParser:
        """Cria e configura o parser de argumentos."""
        parser = argparse.ArgumentParser(
            description="Harmonic Cadence - Análise harmônica de músicas"
        )

        # Subcomandos (analyze, cache, etc)
        subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

        # Comando: analyze
        analyze_parser = subparsers.add_parser(
            "analyze", help="Analisa uma música específica ou todas do artista"
        )
        analyze_parser.add_argument("artist", help="Nome do artista")

        # Argumento song agora é opcional quando --all é usado
        analyze_parser.add_argument(
            "song",
            nargs="?",  # Torna o argumento opcional
            default=None,
            help="Nome da música (omitir quando usar --all)",
        )

        analyze_parser.add_argument(
            "--all",
            action="store_true",
            help="Analisa todas as músicas do artista (em vez de uma específica)",
        )
        analyze_parser.add_argument(
            "--format",
            "-f",
            choices=["html", "json", "markdown"],
            default="json",
            help="Formato do relatório (default: json)",
        )
        analyze_parser.add_argument(
            "--provider",
            choices=["inprocess", "http"],
            default="inprocess",
            help="Origem da cifra: inprocess (sem servidor, padrão) ou http",
        )
        analyze_parser.add_argument(
            "--offline",
            action="store_true",
            help="Prioriza o cache local (não vai à rede se houver cache)",
        )
        analyze_parser.add_argument(
            "--refresh",
            action="store_true",
            help="Força nova busca e reescreve o cache",
        )
        analyze_parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Desativa o cache local",
        )
        analyze_parser.add_argument(
            "--api-url",
            dest="api_url",
            default=None,
            help="URL base da API quando --provider http (default: env/localhost:3000)",
        )
        # Explicação do relatório: template offline (padrão) ou LLM opt-in.
        self._add_llm_flags(analyze_parser)

        # Comando: analyze-file — analisa um arquivo de acordes local (sem Cifra Club).
        # A tonalidade é detectada dos acordes (sem "Tom:" da fonte); não toca a rede.
        file_parser = subparsers.add_parser(
            "analyze-file",
            help="Analisa um arquivo .txt de acordes local (sem scraping)",
        )
        file_parser.add_argument("path", help="Caminho do arquivo de acordes (.txt)")
        file_parser.add_argument(
            "--artist", "-a", default="", help="Artista (opcional; metadado)"
        )
        file_parser.add_argument(
            "--title", "-t", default="", help="Título (opcional; default: nome do arquivo)"
        )
        file_parser.add_argument(
            "--format",
            "-f",
            choices=["html", "json", "markdown"],
            default="json",
            help="Formato do relatório (default: json)",
        )
        self._add_llm_flags(file_parser)

        # Comando: cache
        cache_parser = subparsers.add_parser(
            "cache", help="Baixa e salva músicas para uso offline"
        )
        cache_parser.add_argument(
            "--songs",
            nargs="+",
            help="Lista de músicas no formato 'artista:musica'",
        )
        cache_parser.add_argument(
            "--file",
            "-f",
            help="Arquivo com lista de músicas (uma por linha, formato: artista:musica)",
        )
        cache_parser.add_argument(
            "--artist",
            "-a",
            help="Nome do artista para baixar todas as músicas",
        )
        cache_parser.add_argument(
            "--force",
            action="store_true",
            help="Força download mesmo se já existir no cache",
        )

        # Comando: list
        list_parser = subparsers.add_parser(
            "list", help="Lista as músicas de um artista"
        )
        list_parser.add_argument("artist", help="Nome do artista")
        list_parser.add_argument(
            "--cached",
            action="store_true",
            help="Lista apenas músicas em cache",
        )

        # Comando: explain — explicação pedagógica (template offline ou LLM opt-in)
        explain_parser = subparsers.add_parser(
            "explain", help="Explica a harmonia de uma música em prosa"
        )
        explain_parser.add_argument("artist", help="Nome do artista")
        explain_parser.add_argument("song", help="Nome da música")
        self._add_llm_flags(explain_parser)
        self._add_provider_flags(explain_parser)

        # Comando: reharmonize — sugestões de reharmonização idiomáticas
        reharm_parser = subparsers.add_parser(
            "reharmonize", help="Sugere reharmonizações para uma música"
        )
        reharm_parser.add_argument("artist", help="Nome do artista")
        reharm_parser.add_argument("song", help="Nome da música")
        self._add_provider_flags(reharm_parser)

        # Comando: fingerprint — DNA harmônico de um artista (corpus via --all)
        fp_parser = subparsers.add_parser(
            "fingerprint", help="Impressão digital harmônica de um artista (corpus)"
        )
        fp_parser.add_argument("artist", help="Nome do artista")
        fp_parser.add_argument(
            "--songs",
            nargs="+",
            help="Lista de músicas; omitir para usar todas (--all)",
        )
        fp_parser.add_argument(
            "--all",
            action="store_true",
            help="Usa todas as músicas do artista",
        )
        self._add_provider_flags(fp_parser)

        # Comando: corpus — materializa o corpus local num banco DuckDB e roda gates
        corpus_parser = subparsers.add_parser(
            "corpus", help="Persiste as análises do corpus local e audita os gates"
        )
        corpus_parser.add_argument(
            "action",
            choices=["build", "gates", "report", "anomalies", "similar", "clusters"],
            help="build: materializa cifras/*.md no banco; gates: audita os "
            "invariantes; report: relatório musicológico descritivo (Markdown); "
            "anomalies: worklist de anomalia funcional (overlay Camada C, PRATA); "
            "similar: músicas harmonicamente próximas (--song <slug>); "
            "clusters: famílias harmônicas do corpus (--k N)",
        )
        corpus_parser.add_argument(
            "--song", default=None,
            help="slug da música para `corpus similar` (ex.: 'garota-de-ipanema')",
        )
        corpus_parser.add_argument(
            "--k", type=int, default=10, help="nº de vizinhos (padrão: 10)"
        )
        corpus_parser.add_argument(
            "--db", default="corpus.duckdb", help="Caminho do banco (padrão: corpus.duckdb)"
        )
        corpus_parser.add_argument(
            "--glob", default="cifras/*.md", help="Padrão do corpus local"
        )
        corpus_parser.add_argument(
            "--out", default="corpus-report.md",
            help="Arquivo de saída do report (padrão: corpus-report.md)",
        )

        return parser

    @staticmethod
    def _add_llm_flags(p: argparse.ArgumentParser) -> None:
        """Flags do motor de explicação (template offline padrão; LLM opt-in)."""
        p.add_argument(
            "--engine",
            choices=["template", "llm"],
            default="template",
            help="Motor da explicação: template (offline, padrão) ou llm (opt-in)",
        )
        p.add_argument(
            "--llm-provider",
            dest="llm_provider",
            default="openrouter",
            help="Provedor de LLM (default: openrouter, gratuito)",
        )
        p.add_argument(
            "--llm-model",
            dest="llm_model",
            default=None,
            help="Modelo do provedor (default: o gratuito do provedor)",
        )

    @staticmethod
    def _add_provider_flags(p: argparse.ArgumentParser) -> None:
        """Flags comuns de origem/cache para os subcomandos da Camada 3."""
        p.add_argument(
            "--provider",
            choices=["inprocess", "http"],
            default="inprocess",
            help="Origem da cifra: inprocess (padrão) ou http",
        )
        p.add_argument("--offline", action="store_true", help="Prioriza o cache local")
        p.add_argument("--refresh", action="store_true", help="Força nova busca")
        p.add_argument("--no-cache", action="store_true", help="Desativa o cache")
        p.add_argument(
            "--api-url", dest="api_url", default=None, help="URL base da API (http)"
        )

    def run(self, args: Optional[List[str]] = None) -> None:
        """Executa o CLI com os argumentos fornecidos."""
        if args is None:
            args = sys.argv[1:]

        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self.parser.print_help()
            return

        try:
            if parsed_args.command == "analyze":
                self._handle_analyze(parsed_args)
            elif parsed_args.command == "analyze-file":
                self._handle_analyze_file(parsed_args)
            elif parsed_args.command == "cache":
                self._handle_cache(parsed_args)
            elif parsed_args.command == "list":
                self._handle_list(parsed_args)
            elif parsed_args.command == "explain":
                self._handle_explain(parsed_args)
            elif parsed_args.command == "reharmonize":
                self._handle_reharmonize(parsed_args)
            elif parsed_args.command == "fingerprint":
                self._handle_fingerprint(parsed_args)
            elif parsed_args.command == "corpus":
                self._handle_corpus(parsed_args)
        except Exception as e:
            print(f"Erro: {str(e)}")
            sys.exit(1)

    def _handle_analyze(self, args: argparse.Namespace) -> None:
        if args.all:
            if args.song:
                print("Aviso: O nome da música será ignorado quando usar --all")
            self._handle_analyze_all(args)
        else:
            if not args.song:
                print("Erro: É necessário especificar uma música ou usar --all")
                self.parser.print_help()
                return

            try:
                service = self._build_service(args)
                result = service.analyze_song_from_api(args.artist, args.song)
                if not result or "error" in result:
                    print(
                        f"Música não encontrada ou análise inválida: {args.artist} - {args.song}"
                    )
                    return
                self._apply_explanation_engine(result, args)
                generator = ReportFactory.create(args.format)
                filename = generator.generate(result)
                print(f"\nRelatório gerado com sucesso: {filename}")
            except Exception as e:
                print(f"Erro ao analisar música: {str(e)}")

    def _handle_analyze_file(self, args: argparse.Namespace) -> None:
        """Analisa um arquivo de acordes local — adaptador de entrada NÃO-Cifra-Club.

        Lê o texto, ingere via `cifra_from_text` (mesma normalização do provider) e roda
        o MESMO motor por `analyze_song_data_structured`, sem construir provider de rede.
        Degrada visível: arquivo ausente/vazio/sem acordes → erro claro + saída ≠ 0."""
        try:
            with open(args.path, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            print(f"Erro ao ler o arquivo: {e}")
            sys.exit(1)

        title = args.title or os.path.splitext(os.path.basename(args.path))[0]
        cifra = cifra_from_text(text, artist=args.artist, title=title)

        service = AnalysisService()  # sem provider: caminho local não acessa a rede
        result = service.analyze_song_data_structured(cifra.to_dict())
        if not result or result.get("success") is False or "error" in result:
            msg = (result or {}).get("error", "cifra inválida")
            print(f"Erro ao analisar o arquivo: {msg}")
            sys.exit(1)

        self._apply_explanation_engine(result, args)
        generator = ReportFactory.create(args.format)
        filename = generator.generate(result)
        print(f"\nRelatório gerado com sucesso: {filename}")

    def _handle_analyze_all(self, args: argparse.Namespace) -> None:
        """Analisa todas as músicas de um artista com paralelização."""
        try:
            # Obter lista de músicas
            data = fetch_artist_songs(args.artist)
            songs = [song["name"] for song in data["songs"]]

            print(f"\nIniciando análise de {len(songs)} músicas de {args.artist}...")
            print(f"Formato do relatório: {args.format}")

            # Configurações de paralelismo
            max_workers = min(4, len(songs))
            report_generator = ReportFactory.create(args.format)
            service = self._build_service(args)
            consolidated_results = []
            stats = {"success": 0, "failed": 0, "errors": []}

            def process_song(song: str) -> Optional[Dict]:
                """Função de processamento para paralelização."""
                try:
                    result = service.analyze_song_from_api(args.artist, song)

                    if not result or "error" in result:
                        stats["failed"] += 1
                        stats["errors"].append(f"{song}: Análise inválida")
                        return None

                    self._apply_explanation_engine(result, args, quiet=True)
                    stats["success"] += 1
                    return result

                except Exception as e:
                    stats["failed"] += 1
                    stats["errors"].append(f"{song}: {str(e)}")
                    return None

            # Processamento paralelo
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_song, song) for song in songs]

                with tqdm(total=len(songs), desc="Progresso") as pbar:
                    for future in futures:
                        result = future.result()
                        if result:
                            if hasattr(args, "consolidated") and args.consolidated:
                                consolidated_results.append(result)
                            else:
                                filename = report_generator.generate(result)
                                print(f"  [✓] {result['name']} -> {filename}")
                        pbar.update(1)

            # Geração de relatório consolidado
            if (
                hasattr(args, "consolidated")
                and args.consolidated
                and consolidated_results
            ):
                consolidated_data = {
                    "artist": args.artist,
                    "total_songs": len(songs),
                    "successful_analysis": stats["success"],
                    "failed_analysis": stats["failed"],
                    "songs": consolidated_results,
                    "errors": stats["errors"],
                }
                filename = report_generator.generate(consolidated_data)
                print(f"\nRelatório consolidado gerado: {filename}")

            # Resumo final
            print(f"\nResumo da análise de {args.artist}:")
            print(f"- Músicas analisadas com sucesso: {stats['success']}")
            print(f"- Falhas: {stats['failed']}")

            if stats["failed"] > 0:
                print("\nErros encontrados:")
                for error in stats["errors"][:5]:  # Mostra apenas os 5 primeiros erros
                    print(f"  • {error}")
                if len(stats["errors"]) > 5:
                    print(f"  (... mais {len(stats['errors']) - 5} erros)")

        except Exception as e:
            print(f"\nErro fatal ao analisar músicas do artista: {str(e)}")
            sys.exit(1)

    def _handle_corpus(self, args: argparse.Namespace) -> None:
        """Materializa o corpus local no banco (build) ou audita os gates (gates).

        Import tardio da camada de persistência (traz `duckdb`) — mantém a CLI base
        enxuta, como o explainer LLM."""
        from harmonic_analysis.persistence import build_corpus, init_db

        if args.action == "build":
            conn = init_db(args.db)
            summary = build_corpus(conn, args.glob)
            if summary.get("error"):
                print(summary["error"])
                sys.exit(1)
            print(f"\nCorpus materializado em {args.db}")
            print(f"  run_id={summary['run_id']}  músicas={summary['n_songs']}")
            ledger = conn.execute(
                "SELECT center_status, n FROM v_center_ledger ORDER BY n DESC"
            ).fetchall()
            print("  centro (corroboração):", ", ".join(f"{s}={n}" for s, n in ledger))
            if summary.get("failures"):
                print(f"  falhas (visíveis): {len(summary['failures'])}")
                for f in summary["failures"][:10]:
                    print(f"    - {f}")
            conn.close()
            return

        # gates/report exigem banco populado (falha visível).
        conn = init_db(args.db)
        if conn.execute("SELECT COUNT(*) FROM song").fetchone()[0] == 0:
            print("Banco vazio — rode `harmonic corpus build` primeiro.")
            sys.exit(1)

        if args.action == "report":
            from harmonic_analysis.persistence.report import render_report

            md = render_report(conn)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Relatório musicológico gerado: {args.out}")
            conn.close()
            return

        if args.action == "anomalies":
            # Overlay Camada C (PRATA): materializa a worklist e emite o relatório.
            from harmonic_analysis.overlay.materialize import build_anomaly_worklist
            from harmonic_analysis.overlay.report import render_anomaly_report

            summary = build_anomaly_worklist(conn)
            out = "anomaly-worklist.md" if args.out == "corpus-report.md" else args.out
            md = render_anomaly_report(conn)
            with open(out, "w", encoding="utf-8") as f:
                f.write(md)
            print(
                f"Worklist de anomalia (overlay PRATA) materializada: run "
                f"{summary['run_id']}, {summary['n_occurrences']} ocorrências em "
                f"{summary['n_songs']} músicas."
            )
            print(f"Relatório gerado: {out}  (o ML rankeia; o Chediak adjudica)")
            conn.close()
            return

        if args.action == "similar":
            # Retrieval de similaridade harmônica (Camada C, descritivo).
            from harmonic_analysis.overlay.similarity import (
                build_neighbors,
                fingerprint_from_db,
                neighbors_up_to_date,
                resolve_slug,
                shared_traits,
            )

            if not args.song:
                print("Erro: informe --song <slug> (ex.: --song garota-de-ipanema).")
                conn.close()
                sys.exit(1)
            song_id = resolve_slug(conn, args.song)
            if song_id is None:
                print(
                    f"Música '{args.song}' não está no corpus (run corrente). "
                    "Confira o slug com `harmonic corpus report` ou `openspec`."
                )
                conn.close()
                sys.exit(1)
            if not neighbors_up_to_date(conn):
                build_neighbors(conn, k=max(args.k, 10))
            rows = conn.execute(
                "SELECT neighbor_id, neighbor_title, neighbor_slug, "
                "neighbor_completeness, similarity FROM v_song_neighbor "
                "WHERE song_id = ? ORDER BY rank LIMIT ?",
                [song_id, args.k],
            ).fetchall()
            base_fp = fingerprint_from_db(conn, song_id)
            title = conn.execute(
                "SELECT title FROM v_song_current WHERE song_id = ?", [song_id]
            ).fetchone()[0]
            print(f"\nMúsicas harmonicamente próximas de «{title}» ({args.song})")
            print("(similaridade descritiva por FUNÇÃO — invariante a tom; não é "
                  "juízo de qualidade)\n")
            for nid, ntitle, nslug, ncompl, sim in rows:
                traits = shared_traits(base_fp, fingerprint_from_db(conn, nid))
                partial = "" if ncompl == "complete" else f"  [cifra {ncompl}]"
                shared = ", ".join(traits["functions"]) or "—"
                cad = ", ".join(traits["cadences"]) or "—"
                print(f"  {sim:.3f}  {ntitle} ({nslug}){partial}")
                print(f"         funções em comum: {shared} · cadências: {cad}")
            conn.close()
            return

        if args.action == "clusters":
            # Famílias harmônicas do corpus (Camada C, descritivo).
            from harmonic_analysis.overlay.clustering import (
                build_clusters,
                cluster_traits,
                corpus_baseline,
            )

            summary = build_clusters(conn, k=args.k)
            baseline = corpus_baseline(conn)
            print(
                f"\n{summary['k']} famílias harmônicas sobre {summary['n_songs']} "
                f"músicas (k escolhido pelo usuário — descritivo, NÃO 'k ótimo'; "
                "família ≠ qualidade)\n"
            )
            rows = conn.execute(
                "SELECT cluster_id, song_id, song_title, song_slug, "
                "completeness, is_medoid FROM v_song_cluster ORDER BY cluster_id, "
                "is_medoid DESC, song_title"
            ).fetchall()
            from itertools import groupby

            for cid, group in groupby(rows, key=lambda r: r[0]):
                members = list(group)
                ids = [m[1] for m in members]
                traits = cluster_traits(conn, ids, baseline)
                medoid = next((m for m in members if m[5]), members[0])
                print(f"Família {cid} — {len(members)} músicas · "
                      f"protótipo: «{medoid[2]}» ({medoid[3]})")
                if not traits["functions"] and not traits["cadences"]:
                    print("  traços: — família-baseline (nada acima da média do corpus)")
                else:
                    fn = ", ".join(
                        f"{k} (+{v})" for k, v in traits["functions"]
                    ) or "—"
                    cad = ", ".join(
                        f"{k} (+{v})" for k, v in traits["cadences"]
                    ) or "—"
                    print(f"  distingue-se por (lift vs. corpus): funções {fn} · "
                          f"cadências {cad}")
                shown = [m for m in members if not m[5]][:6]
                for _cid, _sid, title, slug, compl, _med in shown:
                    tag = "" if compl == "complete" else f"  [cifra {compl}]"
                    print(f"    · {title} ({slug}){tag}")
                if len(members) - 1 > len(shown):
                    print(f"    … +{len(members) - 1 - len(shown)} músicas")
                print()
            conn.close()
            return
        gates = {
            "diminuto (XXI-XXII)": "v_gate_diminished",
            "D2 resolução (XIX)": "v_gate_d2",
            "cadência×função (XXXII)": "v_gate_cadence",
        }
        total = 0
        print("\nGates EXECUTÁVEIS (Chediak; vazio = verde):")
        for label, view in gates.items():
            rows = conn.execute(f"SELECT * FROM {view}").fetchall()
            total += len(rows)
            status = "VERDE" if not rows else f"{len(rows)} VIOLAÇÕES"
            print(f"  {label:<26} {status}")
            for r in rows[:5]:
                print(f"      {r}")
        ledger = conn.execute(
            "SELECT COUNT(*) FROM v_ledger_tritone_nondominant"
        ).fetchone()[0]
        print(
            f"\nLEDGER trítono→não-dominante (curadoria, NÃO gate): {ledger} ocorrências"
        )
        print("  (I7 tônico de blues/funk + empréstimo modal — adjudicação Chediak"
              " em change separada)")
        conn.close()
        sys.exit(1 if total else 0)

    def _handle_cache(self, args: argparse.Namespace) -> None:
        """Processa o comando de cache."""
        # Se --artist foi especificado, baixa todas as músicas do artista
        if args.artist:
            try:
                total, success = cache_all_artist_songs(args.artist, force=args.force)
                print(f"\nResumo do artista {args.artist}:")
                print(f"- Total de músicas: {total}")
                print(f"- Músicas baixadas com sucesso: {success}")
                print(f"- Falhas: {total - success}")
                return
            except Exception as e:
                print(f"Erro ao baixar músicas do artista {args.artist}: {e}")
                sys.exit(1)

        # Processa músicas individuais
        songs_to_cache = []

        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    songs_to_cache.extend(line.strip() for line in f if line.strip())
            except Exception as e:
                print(f"Erro ao ler arquivo {args.file}: {e}")
                sys.exit(1)

        if args.songs:
            songs_to_cache.extend(args.songs)

        if not songs_to_cache:
            print("Nenhuma música especificada para cache.")
            sys.exit(1)

        success = 0
        failed = 0

        for entry in songs_to_cache:
            if ":" not in entry:
                print(f"Formato inválido: {entry}. Use 'artista:musica'")
                failed += 1
                continue

            artist, song = entry.split(":", 1)
            try:
                if download_and_cache_song(
                    artist.strip(), song.strip(), force=args.force
                ):
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Erro ao baixar {artist} - {song}: {e}")
                failed += 1

        print("\nResumo:")
        print(f"- Músicas baixadas com sucesso: {success}")
        print(f"- Falhas: {failed}")

    def _handle_list(self, args: argparse.Namespace) -> None:
        """Lista as músicas de um artista."""
        try:
            if args.cached:
                # Lista músicas do cache
                songs = load_artist_songs(args.artist)
            else:
                # Busca lista atualizada da API
                data = fetch_artist_songs(args.artist)
                songs = [song["name"] for song in data["songs"]]

            print(f"\nMúsicas de {args.artist}:")
            for i, song in enumerate(songs, 1):
                print(f"{i:3d}. {song}")
            print(f"\nTotal: {len(songs)} músicas")

        except Exception as e:
            print(f"Erro ao listar músicas: {e}")
            sys.exit(1)


    @staticmethod
    def _load_dotenv(path: str = ".env") -> None:
        """Carrega variáveis de um `.env` no ambiente (só as ainda não definidas).

        Mínimo e sem dependência: variáveis já presentes no ambiente têm
        prioridade. Permite que a chave do LLM (ex.: OPENROUTER_API_KEY) deixada
        no `.env` seja usada pelo CLI sem `export` manual.
        """
        import os

        if not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ.setdefault(
                        key.strip(), value.strip().strip('"').strip("'")
                    )
        except OSError:
            pass

    @staticmethod
    def _llm_unavailable_hint(llm_cfg) -> str:
        """Mensagem específica do porquê o LLM caiu no template (dep/chave/provedor)."""
        from harmonic_analysis.explain import (
            MissingCredentials,
            MissingDependency,
            build_llm_provider,
        )

        try:
            build_llm_provider(llm_cfg).preflight()
            return "motor LLM indisponível — usando template offline."
        except MissingDependency:
            return (
                "motor LLM indisponível: dependência ausente. Rode com o extra, "
                "ex.: `uv run --extra explain-llm harmonic ...`. Usando template offline."
            )
        except MissingCredentials:
            return (
                "motor LLM indisponível: defina a chave do provedor "
                "(ex.: OPENROUTER_API_KEY, inclusive via .env) ou use "
                "`--llm-provider ollama`. Usando template offline."
            )
        except KeyError:
            return (
                f"motor LLM indisponível: provedor '{llm_cfg.provider}' desconhecido. "
                "Usando template offline."
            )

    def _apply_explanation_engine(
        self, result: Dict, args: argparse.Namespace, quiet: bool = False
    ) -> None:
        """Quando `--engine llm`, regenera a seção `explanation` via LLM.

        O serviço já preencheu `explanation` com o template (offline). Aqui, sob
        opt-in explícito, substituímos pela versão do LLM — com fallback gracioso:
        sem extra/chave/provedor cai no template; falha de rede mantém o template.
        """
        if getattr(args, "engine", "template") != "llm":
            return
        if not result or "error" in result:
            return

        self._load_dotenv()  # pega OPENROUTER_API_KEY etc. do .env, se existir

        from harmonic_analysis.explain import (
            ExplainConfig,
            LLMConfig,
            build_explainer,
        )

        cfg = ExplainConfig(
            engine="llm",
            llm=LLMConfig(
                provider=getattr(args, "llm_provider", "openrouter"),
                model=getattr(args, "llm_model", None),
            ),
        )
        explainer = build_explainer(cfg)
        if type(explainer).__name__ == "TemplateExplainer":
            if not quiet:
                print(f"Aviso: {self._llm_unavailable_hint(cfg.llm)}")
            return  # result['explanation'] já é o template
        try:
            result["explanation"] = explainer.explain(result)
        except Exception as e:  # falha de rede/modelo → mantém o template
            if not quiet:
                print(f"Aviso: falha ao gerar explicação via LLM ({e}); usando template.")

    def _handle_explain(self, args: argparse.Namespace) -> None:
        """Explicação pedagógica — template offline (padrão) ou LLM opt-in."""
        from harmonic_analysis.explain import (
            ExplainConfig,
            LLMConfig,
            build_explainer,
        )

        if args.engine == "llm":
            self._load_dotenv()  # pega a chave do .env, se existir

        service = self._build_service(args)
        result = service.analyze_song_from_api(args.artist, args.song)
        if not result or "error" in result:
            print(f"Música não encontrada ou análise inválida: {args.artist} - {args.song}")
            return

        cfg = ExplainConfig(
            engine=args.engine,
            llm=LLMConfig(provider=args.llm_provider, model=args.llm_model),
        )
        explainer = build_explainer(cfg)
        if args.engine == "llm" and type(explainer).__name__ == "TemplateExplainer":
            print(f"Aviso: {self._llm_unavailable_hint(cfg.llm)}")
        print(f"\n{explainer.explain(result)}\n")

    def _handle_reharmonize(self, args: argparse.Namespace) -> None:
        """Imprime as sugestões de reharmonização de uma música."""
        service = self._build_service(args)
        result = service.analyze_song_from_api(args.artist, args.song)
        if not result or "error" in result:
            print(f"Música não encontrada ou análise inválida: {args.artist} - {args.song}")
            return

        suggestions = result.get("reharmonizations") or []
        if not suggestions:
            print("Nenhuma sugestão de reharmonização encontrada.")
            return
        print(f"\nReharmonizações para {result['name']} ({result['key']} {result['mode']}):")
        for s in suggestions:
            arrow = " ".join(s["original"]) + " → " + " ".join(s["result"])
            print(f"  • [{s['technique']}] {arrow}")
            print(f"    {s['rationale']}")

    def _handle_fingerprint(self, args: argparse.Namespace) -> None:
        """Impressão digital harmônica de um artista (agregada sobre o corpus)."""
        from harmonic_analysis.domain.style_fingerprint import build_fingerprint

        service = self._build_service(args)
        if args.songs:
            song_names = args.songs
        else:
            data = fetch_artist_songs(args.artist)
            song_names = [song["name"] for song in data["songs"]]

        results = []
        for name in song_names:
            r = service.analyze_song_from_api(args.artist, name)
            if r and "error" not in r:
                results.append(r)

        if not results:
            print(f"Nenhuma análise válida para {args.artist}.")
            return

        fp = build_fingerprint(results).to_dict()
        print(f"\nImpressão digital harmônica de {args.artist} ({fp['song_count']} músicas):")
        print("  Distribuição de funções:")
        for func, weight in sorted(fp["function_distribution"].items(), key=lambda x: -x[1]):
            print(f"    {func:6} {weight:.1%}")
        print(f"  Cadências: {fp['cadence_counts']}")
        print(f"  Uso modal: {fp['modal_usage']:.1%}")
        print(f"  Densidade de tensões: {fp['tension_density']:.1%}")


def main():
    """Função principal do CLI."""
    cli = HarmonicCLI()
    cli.run()


if __name__ == "__main__":
    main()
