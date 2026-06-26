from __future__ import annotations

import json
import os
import tempfile
from enum import Enum, auto
from typing import List, Optional, Protocol

from cifra_core.exceptions import ProviderUnavailable
from cifra_core.models import Cifra, SongRef
from cifra_core.provider import SongProvider
from cifra_core.slug import slugify


class CachePolicy(Enum):
    NETWORK_FIRST = auto()  # rede; cai para o cache se indisponível (padrão)
    CACHE_FIRST = auto()    # cache; só vai à rede no miss
    CACHE_ONLY = auto()     # nunca toca a rede
    REFRESH = auto()        # força rede e reescreve o cache


class CacheStore(Protocol):
    def get(self, key: str) -> Optional[Cifra]: ...
    def put(self, key: str, cifra: Cifra) -> None: ...


def cache_key(artist: str, song: str) -> str:
    return f"{slugify(artist)}_{slugify(song)}"


class JsonFileCacheStore:
    """Persiste cada Cifra como `{slug}.json`, com escrita atômica."""

    def __init__(self, directory: str):
        self.directory = directory

    def _path(self, key: str) -> str:
        return os.path.join(self.directory, f"{key}.json")

    def get(self, key: str) -> Optional[Cifra]:
        path = self._path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return Cifra.from_api(json.load(f))
        except Exception:
            return None

    def put(self, key: str, cifra: Cifra) -> None:
        os.makedirs(self.directory, exist_ok=True)
        # escrita atômica: grava em tmp e renomeia (os.replace é atômico)
        fd, tmp = tempfile.mkstemp(dir=self.directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(cifra.to_dict(), f, ensure_ascii=False, indent=2)
            os.replace(tmp, self._path(key))
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise


class CachingSongProvider:
    """Decorator que adiciona cache a um SongProvider, governado por CachePolicy."""

    def __init__(
        self,
        inner: SongProvider,
        store: CacheStore,
        policy: CachePolicy = CachePolicy.NETWORK_FIRST,
    ):
        self.inner = inner
        self.store = store
        self.policy = policy

    def get_song(self, artist: str, song: str) -> Cifra:
        key = cache_key(artist, song)

        # Modos que consultam o cache primeiro.
        if self.policy in (CachePolicy.CACHE_FIRST, CachePolicy.CACHE_ONLY):
            cached = self.store.get(key)
            if cached is not None:
                return cached
            if self.policy is CachePolicy.CACHE_ONLY:
                raise ProviderUnavailable(
                    f"Sem cache para {artist} - {song} (CACHE_ONLY)"
                )
            # CACHE_FIRST miss → segue para a rede

        try:
            cifra = self.inner.get_song(artist, song)
        except ProviderUnavailable:
            # REFRESH não usa fallback; demais modos tentam o cache.
            if self.policy is not CachePolicy.REFRESH:
                cached = self.store.get(key)
                if cached is not None:
                    return cached
            raise
        # Sucesso → write-through. Negativos já levantaram e nunca chegam aqui.
        self.store.put(key, cifra)
        return cifra

    def list_artist_songs(self, artist: str) -> List[SongRef]:
        return self.inner.list_artist_songs(artist)
