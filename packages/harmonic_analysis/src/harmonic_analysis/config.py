import os
from dataclasses import dataclass, field

from cifra_core import (
    CachePolicy,
    CachingSongProvider,
    JsonFileCacheStore,
    SongProvider,
)


@dataclass
class ProviderConfig:
    """Configuração da raiz de composição — único lugar que conhece config."""

    kind: str = "inprocess"  # "inprocess" | "http"
    cache_enabled: bool = True
    cache_policy: CachePolicy = CachePolicy.NETWORK_FIRST
    cache_dir: str = field(
        default_factory=lambda: os.environ.get("HARMONIC_CACHE_DIR", "data")
    )
    api_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "HARMONIC_API_URL", "http://localhost:3000"
        )
    )


def build_song_provider(cfg: ProviderConfig) -> SongProvider:
    """Monta o SongProvider ativo a partir da config.

    O domínio e os serviços dependem apenas da porta; só esta função
    importa os adaptadores concretos. O import do scraper é tardio para
    manter o caminho HTTP independente do extra ``[inprocess]``.
    """
    if cfg.kind == "http":
        from harmonic_analysis.infra.http_provider import HttpSongProvider

        inner: SongProvider = HttpSongProvider(cfg.api_base_url)
    else:
        from cifra_scraper.song_provider import InProcessSongProvider

        inner = InProcessSongProvider()

    if cfg.cache_enabled:
        inner = CachingSongProvider(
            inner, JsonFileCacheStore(cfg.cache_dir), cfg.cache_policy
        )
    return inner
