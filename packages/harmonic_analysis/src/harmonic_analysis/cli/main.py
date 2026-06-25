import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

from tqdm import tqdm

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
        self.analysis_service = AnalysisService()

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

        return parser

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
            elif parsed_args.command == "cache":
                self._handle_cache(parsed_args)
            elif parsed_args.command == "list":
                self._handle_list(parsed_args)
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
                result = self.analysis_service.analyze_song_from_api(
                    args.artist, args.song
                )
                if not result or "error" in result:
                    print(
                        f"Música não encontrada ou análise inválida: {args.artist} - {args.song}"
                    )
                    return
                generator = ReportFactory.create(args.format)
                filename = generator.generate(result)
                print(f"\nRelatório gerado com sucesso: {filename}")
            except Exception as e:
                print(f"Erro ao analisar música: {str(e)}")

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
            consolidated_results = []
            stats = {"success": 0, "failed": 0, "errors": []}

            def process_song(song: str) -> Optional[Dict]:
                """Função de processamento para paralelização."""
                try:
                    result = self.analysis_service.analyze_song_from_api(
                        args.artist, song
                    )

                    if not result or "error" in result:
                        stats["failed"] += 1
                        stats["errors"].append(f"{song}: Análise inválida")
                        return None

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


def main():
    """Função principal do CLI."""
    cli = HarmonicCLI()
    cli.run()


if __name__ == "__main__":
    main()
