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
- relativa-consciente (perdoa a confusão maior ↔ relativa menor);
- coleção/armadura (a tônica detectada é um grau diatônico do gold).

Uso:  uv run python scripts/key_baseline.py   (precisa de rede)
"""

import re

from cifra_core import ChordPattern
from cifra_scraper.song_provider import InProcessSongProvider

from harmonic_analysis.domain.key_detection import detect_key
from harmonic_analysis.validation import (
    center_ok,
    evaluate_modulating_song,
    is_relative,
    parse_key,
    same_collection,
)

# ruff: noqa: E402 — scripts/ não é pacote; ajusta sys.path se rodado direto
try:
    from scripts.chediak_structural_gold import verify_tonal_center
except ModuleNotFoundError:  # rodado como `python scripts/key_baseline.py`
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.chediak_structural_gold import verify_tonal_center

# (artista, música, tom-Cifra Club) — anotação da própria fonte (fato público).
# Curado raspando de fato; só entram as que scrapam com tom anotado. Inclui casos
# difíceis (confusão relativa E paralela) de propósito — um baseline não cherry-pick.
# Entradas com 4 elementos `(artista, música, primária, [secundárias])` são músicas
# MODULANTES (Chediak p. 118, modulação por acorde pivô): medidas à parte, com
# acerto parcial/total, e FORA das métricas agregadas monotonais.
GOLD = [
    ("Tom Jobim", "Garota de Ipanema", "F"),
    ("Tom Jobim", "Wave", "Dm", ["D"]),
    ("Tom Jobim", "Aguas de Marco", "B"),
    ("Tom Jobim", "Corcovado", "Am"),
    ("Tom Jobim", "Insensatez", "Bm"),
    ("Tom Jobim", "Desafinado", "A"),
    ("Tom Jobim", "Chega de Saudade", "Dm", ["D"]),
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


def _key_str(k) -> str:
    return f"{_PC[k[0]]} {k[1][:3]}"


def main() -> None:
    provider = InProcessSongProvider()
    results = []          # músicas monotonais: (música, anotado, detectado)
    modulating = []       # músicas modulantes: MultiKeyEval
    # centro estrutural (Chediak): (música, det, cc_key, offset, provenance)
    center = []
    for entry in GOLD:
        artist, song, gold = entry[0], entry[1], entry[2]
        secondaries = entry[3] if len(entry) > 3 else None
        try:
            cifra = provider.get_song(artist, song)
            chords = _chords(cifra.cifra)
        except Exception as exc:  # noqa: BLE001 — scraping pode falhar (404, rede)
            print(f"  ! {song}: falhou ({type(exc).__name__})")
            continue
        if secondaries is not None:  # música modulante → métrica multi-região
            ev = evaluate_modulating_song(song, chords, gold, secondaries)
            if ev is not None:
                modulating.append(ev)
            continue
        ann = parse_key(gold)
        est = detect_key(chords)
        if est is None or ann is None:
            continue
        det = (est.tonic_pc, est.mode)
        results.append((song, ann, det))
        # Centro estrutural TONAL (Tier B): cc_key é só âncora; só conta se um V7/SubV7
        # funcional (trítono, Chediak p.84/87) resolve nele → cc_key É a tônica (offset
        # 0, verified). Senão, quarentena (unverified). O centro MODAL (Tier A, citado)
        # fica para a change 2, que trata a transposição Chediak↔Cifra Club direito.
        ok, _ = verify_tonal_center(chords, ann[0])
        if ok:
            center.append((song, det, ann, 0, "verified"))

    if not results and not modulating:
        print("Nenhuma música avaliada (rede?).")
        return

    n = len(results)
    if n:
        mode = sum(a[1] == d[1] for _, a, d in results) / n
        exact = sum(a == d for _, a, d in results) / n
        rel = sum(a == d or is_relative(a, d) for _, a, d in results) / n
        coll = sum(same_collection(a, d) for _, a, d in results) / n

        print(f"\n{'música':<28}{'fonte':<9}{'detectado':<11}{'resultado'}")
        print("-" * 60)
        for song, a, d in results:
            if a == d:
                verdict = "exato"
            elif is_relative(a, d):
                verdict = "relativo"
            elif a[1] == d[1]:
                verdict = "modo ok"
            elif same_collection(a, d):
                verdict = "coleção"
            else:
                verdict = "ERRO"
            print(f"{song[:27]:<28}{_key_str(a):<9}{_key_str(d):<11}{verdict}")

        print(f"\nBaseline vs tom da fonte (Cifra Club) (n={n}, monotonais):")
        print(f"  modo:                {mode:.0%}")
        print(f"  tonica exata:        {exact:.0%}")
        print(f"  relativa-consciente: {rel:.0%}")
        print(f"  coleção (armadura):  {coll:.0%}")

    # Centro estrutural TONAL — SÓ sobre o subconjunto verificado por dominante funcional
    # (offset 0). O centro MODAL fica para a change 2. Esse é o "buraco" que o gate do
    # trítono vai atacar; as 4 métricas Cifra-Club acima ficam idênticas.
    if center:
        nc = len(center)
        hits = sum(center_ok(det, cc, off) for _, det, cc, off, _ in center)
        print(f"\nCentro estrutural TONAL (verificados por dominante funcional, n={nc}):")
        print(f"  acerto de centro:    {hits / nc:.0%}  ({hits}/{nc})")
        print("\n  buraco de centro (detector pegou outro grau, ex.: o V):")
        for song, det, cc, off, _prov in center:
            if not center_ok(det, cc, off):
                print(
                    f"    {song[:27]:<28}cc(tônica real)={_key_str(cc):<9}"
                    f"det={_key_str(det)}"
                )

    # Músicas modulantes (Chediak p. 118) — medidas à parte: NÃO entram nas
    # métricas agregadas acima, para não distorcer o baseline monotonal.
    if modulating:
        print(f"\n{'música modulante':<28}{'gold':<14}{'regiões':<22}{'acerto'}")
        print("-" * 76)
        for ev in modulating:
            gold_s = "/".join(_key_str(k) for k in (ev.primary_gold, *ev.secondary_golds))
            regs = ", ".join(_key_str(k) for k in ev.detected_regions) or "-"
            if ev.all_ok:
                verdict = "total"
            elif ev.primary_ok:
                verdict = "parcial"
            else:
                verdict = "ERRO"
            print(f"{ev.name[:27]:<28}{gold_s:<14}{regs[:21]:<22}{verdict}")
        n_mod = len(modulating)
        partial = sum(ev.primary_ok for ev in modulating) / n_mod
        total = sum(ev.all_ok for ev in modulating) / n_mod
        print(f"\nModulantes (n={n_mod}):")
        print(f"  acerto parcial (primária): {partial:.0%}")
        print(f"  acerto total (multi-região): {total:.0%}")


if __name__ == "__main__":
    main()
