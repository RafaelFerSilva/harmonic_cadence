"""Baseline de acurácia da detecção de tonalidade contra o ouro do Chediak.

Scrapa os acordes do Cifra Club e compara o tom detectado com o tom anotado por
Almir Chediak (Vol. I) — que é um **fato** (não protegido por copyright). As
cifras NÃO são armazenadas; o corpus é re-scrapado a cada execução.

Métricas (a relativa-consciente é a mais honesta dada a transposição entre a
versão do Cifra Club e a análise do Chediak):
- modo (maior/menor) — invariante à transposição;
- tônica exata;
- relativa-consciente (perdoa a confusão maior ↔ relativa menor).

Uso:  uv run python scripts/key_baseline.py   (precisa de rede)
"""

import re

from cifra_core import ChordPattern
from cifra_scraper.song_provider import InProcessSongProvider

from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.validation import is_relative, parse_key

# (artista, música, tom-Chediak) — anotações de tonalidade do Vol. I (fatos).
GOLD = [
    ("Vinicius de Moraes", "Eu Sei Que Vou Te Amar", "C"),
    ("Joao Bosco", "Papel Marche", "C"),
    ("Joao Bosco", "O Bebado e o Equilibrista", "A"),
    ("Milton Nascimento", "Coracao de Estudante", "F"),
    ("Chico Buarque", "Valsinha", "Am"),
    ("Chico Buarque", "Atras da Porta", "Bm"),
    ("Chico Buarque", "Joao e Maria", "Am"),
    ("Tom Jobim", "Retrato em Branco e Preto", "Gm"),
    ("Luiz Bonfa", "Manha de Carnaval", "Am"),
]

_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_TAG = re.compile(r"<[^>]+>")


def _chords(cifra):
    return [
        s for line in cifra for s in ChordPattern.find_all(_TAG.sub("", line)) if s
    ]


def main() -> None:
    provider = InProcessSongProvider()
    results = []
    for artist, song, gold in GOLD:
        ann = parse_key(gold)
        try:
            cifra = provider.get_song(artist, song)
            est = detect_key(_chords(cifra.cifra))
        except Exception as exc:  # noqa: BLE001 — scraping pode falhar (404, rede)
            print(f"  ! {song}: falhou ({type(exc).__name__})")
            continue
        if est is None or ann is None:
            continue
        det = (est.tonic_pc, est.mode)
        results.append((song, ann, det))

    if not results:
        print("Nenhuma música avaliada (rede?).")
        return

    n = len(results)
    mode = sum(a[1] == d[1] for _, a, d in results) / n
    exact = sum(a == d for _, a, d in results) / n
    rel = sum(a == d or is_relative(a, d) for _, a, d in results) / n

    print(f"\n{'música':<28}{'Chediak':<9}{'detectado':<11}{'resultado'}")
    print("-" * 60)
    for song, a, d in results:
        if a == d:
            verdict = "exato"
        elif is_relative(a, d):
            verdict = "relativo"
        elif a[1] == d[1]:
            verdict = "modo ok"
        else:
            verdict = "ERRO"
        ann_s = f"{_PC[a[0]]} {a[1][:3]}"
        det_s = f"{_PC[d[0]]} {d[1][:3]}"
        print(f"{song[:27]:<28}{ann_s:<9}{det_s:<11}{verdict}")

    print(f"\nBaseline vs ouro Chediak (n={n}):")
    print(f"  modo:                {mode:.0%}")
    print(f"  tonica exata:        {exact:.0%}")
    print(f"  relativa-consciente: {rel:.0%}")


if __name__ == "__main__":
    main()
