"""Baseline de acurácia da detecção de tonalidade, contra o tom da própria fonte.

Scrapa os acordes do Cifra Club e compara o tom **detectado** com o tom **anotado
pelo próprio Cifra Club** (a "tom" da página). Por virem da mesma fonte, NÃO há
gap de transposição — a tônica-exata é uma métrica honesta de primeira classe. O
corpus é uma lista de **fatos** (artista, música, tom); as cifras NÃO são
armazenadas — re-scrapadas a cada execução (corpus independente, dentro da
fronteira de copyright: a Parte 4 do Chediak não é ingerida como fixture).

Métricas:
- modo (maior/menor);
- tônica exata (significativa: ouro e acordes vêm da mesma fonte);
- relativa-consciente (perdoa a confusão maior ↔ relativa menor).

Uso:  uv run python scripts/key_baseline.py   (precisa de rede)
"""

import re

from cifra_core import ChordPattern
from cifra_scraper.song_provider import InProcessSongProvider

from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.validation import is_relative, parse_key

# (artista, música, tom-Cifra Club) — anotação da própria fonte (fato público).
# Curado raspando de fato; só entram as que scrapam com tom anotado. Inclui casos
# difíceis (confusão relativa E paralela) de propósito — um baseline não cherry-pick.
GOLD = [
    ("Tom Jobim", "Garota de Ipanema", "F"),
    ("Tom Jobim", "Wave", "Dm"),
    ("Tom Jobim", "Aguas de Marco", "B"),
    ("Tom Jobim", "Corcovado", "Am"),
    ("Tom Jobim", "Insensatez", "Bm"),
    ("Tom Jobim", "Desafinado", "A"),
    ("Tom Jobim", "Chega de Saudade", "Dm"),
    ("Tom Jobim", "Triste", "G"),
    ("Djavan", "Sina", "A"),
    ("Djavan", "Oceano", "D"),
    ("Djavan", "Flor de Lis", "C"),
    ("Djavan", "Samurai", "C#m"),
    ("Chico Buarque", "Construcao", "Em"),
    ("Chico Buarque", "Roda Viva", "Bm"),
    ("Chico Buarque", "A Banda", "D"),
    ("Chico Buarque", "Calice", "E"),
    ("Chico Buarque", "Valsinha", "Cm"),
    ("Chico Buarque", "Atras da Porta", "E"),
    ("Caetano Veloso", "Sozinho", "D"),
    ("Caetano Veloso", "Sampa", "C"),
    ("Caetano Veloso", "O Leaozinho", "C"),
    ("Gilberto Gil", "Aquele Abraco", "E"),
    ("Gilberto Gil", "Esperando na Janela", "E"),
    ("Milton Nascimento", "Travessia", "A"),
    ("Milton Nascimento", "Coracao de Estudante", "F"),
    ("Joao Bosco", "Papel Marche", "C"),
    ("Cartola", "As Rosas Nao Falam", "Dm"),
    ("Vinicius de Moraes", "Eu Sei Que Vou Te Amar", "Em"),
    # Leva 2 (ampliação do corpus; mesma metodologia, curadas raspando).
    ("Tom Jobim", "A Felicidade", "Bb"),
    ("Tom Jobim", "Dindi", "C"),
    ("Tom Jobim", "So Danco Samba", "Db"),
    ("Tom Jobim", "Samba de Uma Nota So", "G"),
    ("Tom Jobim", "Fotografia", "C"),
    ("Tom Jobim", "Falando de Amor", "Bb"),
    ("Djavan", "Lilas", "C"),
    ("Djavan", "Acai", "G"),
    ("Djavan", "Esquinas", "F"),
    ("Djavan", "Petala", "A"),
    ("Djavan", "Nem Um Dia", "Dm"),
    ("Chico Buarque", "Tatuagem", "C"),
    ("Chico Buarque", "Cotidiano", "Bb"),
    ("Chico Buarque", "Apesar de Voce", "D"),
    ("Chico Buarque", "Trocando em Miudos", "C"),
    ("Chico Buarque", "Carolina", "E"),
    ("Chico Buarque", "Vai Passar", "C"),
    ("Caetano Veloso", "Coracao Vagabundo", "Eb"),
    ("Caetano Veloso", "Cajuina", "Cm"),
    ("Caetano Veloso", "Menino do Rio", "F"),
    ("Gilberto Gil", "Drao", "C"),
    ("Gilberto Gil", "Tempo Rei", "G"),
    ("Gilberto Gil", "Andar com Fe", "C"),
    ("Gilberto Gil", "Realce", "A"),
    ("Milton Nascimento", "Maria Maria", "Ab"),
    ("Milton Nascimento", "Cancao da America", "G"),
    ("Milton Nascimento", "Nada Sera Como Antes", "A"),
    ("Ivan Lins", "Comecar de Novo", "A"),
    ("Ivan Lins", "Novo Tempo", "A"),
    ("Toquinho", "Aquarela", "G"),
    ("Baden Powell", "Canto de Ossanha", "Dm"),
    ("Edu Lobo", "Pra Dizer Adeus", "Bb"),
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

    print(f"\n{'música':<28}{'fonte':<9}{'detectado':<11}{'resultado'}")
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

    print(f"\nBaseline vs tom da fonte (Cifra Club) (n={n}):")
    print(f"  modo:                {mode:.0%}")
    print(f"  tonica exata:        {exact:.0%}")
    print(f"  relativa-consciente: {rel:.0%}")


if __name__ == "__main__":
    main()
