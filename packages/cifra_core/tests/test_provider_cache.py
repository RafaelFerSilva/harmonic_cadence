import pytest

import cifra_core.cache as cache_mod
from cifra_core import (
    CachePolicy,
    CachingSongProvider,
    Cifra,
    JsonFileCacheStore,
    ProviderUnavailable,
    SongNotFound,
    cache_key,
)

C = Cifra(artist="Djavan", name="Sina", cifra=("C  Am", "F  G"))
KEY = cache_key("Djavan", "Sina")


class FakeProvider:
    def __init__(self, result=None, exc=None):
        self.calls = 0
        self.result = result
        self.exc = exc

    def get_song(self, artist, song):
        self.calls += 1
        if self.exc:
            raise self.exc
        return self.result

    def list_artist_songs(self, artist):
        return []


class MemStore:
    def __init__(self):
        self.d = {}

    def get(self, key):
        return self.d.get(key)

    def put(self, key, cifra):
        self.d[key] = cifra


def test_network_first_returns_fresh_and_writes_through():
    store, inner = MemStore(), FakeProvider(result=C)
    cp = CachingSongProvider(inner, store, CachePolicy.NETWORK_FIRST)
    assert cp.get_song("Djavan", "Sina") == C
    assert store.get(KEY) == C


def test_network_first_falls_back_to_cache_on_unavailable():
    store = MemStore()
    store.put(KEY, C)
    cp = CachingSongProvider(
        FakeProvider(exc=ProviderUnavailable("down")), store, CachePolicy.NETWORK_FIRST
    )
    assert cp.get_song("Djavan", "Sina") == C


def test_cache_first_serves_without_calling_inner():
    store = MemStore()
    store.put(KEY, C)
    inner = FakeProvider(result=C)
    cp = CachingSongProvider(inner, store, CachePolicy.CACHE_FIRST)
    assert cp.get_song("Djavan", "Sina") == C
    assert inner.calls == 0


def test_cache_first_hits_network_on_miss_and_writes():
    store, inner = MemStore(), FakeProvider(result=C)
    cp = CachingSongProvider(inner, store, CachePolicy.CACHE_FIRST)
    assert cp.get_song("Djavan", "Sina") == C
    assert inner.calls == 1
    assert store.get(KEY) == C


def test_cache_only_never_calls_network_and_raises_on_miss():
    inner = FakeProvider(result=C)
    cp = CachingSongProvider(inner, MemStore(), CachePolicy.CACHE_ONLY)
    with pytest.raises(ProviderUnavailable):
        cp.get_song("Djavan", "Sina")
    assert inner.calls == 0


def test_refresh_overwrites_even_when_cached():
    store = MemStore()
    store.put(KEY, Cifra(artist="Djavan", name="Sina", cifra=("OLD",)))
    inner = FakeProvider(result=C)
    cp = CachingSongProvider(inner, store, CachePolicy.REFRESH)
    assert cp.get_song("Djavan", "Sina") == C
    assert inner.calls == 1
    assert store.get(KEY) == C


def test_negatives_are_not_cached():
    store = MemStore()
    cp = CachingSongProvider(
        FakeProvider(exc=SongNotFound("Djavan", "X")), store, CachePolicy.NETWORK_FIRST
    )
    with pytest.raises(SongNotFound):
        cp.get_song("Djavan", "X")
    assert store.get(cache_key("Djavan", "X")) is None


def test_json_store_atomic_roundtrip_no_tmp_leftover(tmp_path):
    store = JsonFileCacheStore(str(tmp_path))
    store.put(KEY, C)
    assert store.get(KEY) == C
    assert [p for p in tmp_path.iterdir() if p.suffix == ".tmp"] == []


def test_interrupted_write_keeps_previous_entry(tmp_path, monkeypatch):
    store = JsonFileCacheStore(str(tmp_path))
    store.put(KEY, C)

    def boom(*a, **k):
        raise IOError("disk full")

    monkeypatch.setattr(cache_mod.json, "dump", boom)
    with pytest.raises(IOError):
        store.put(KEY, Cifra(artist="Djavan", name="Sina", cifra=("NEW",)))
    assert store.get(KEY) == C  # entrada anterior intacta
    assert [p for p in tmp_path.iterdir() if p.suffix == ".tmp"] == []
