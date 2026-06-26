"""O modelo Cifra carrega o tom da fonte (`key`)."""

from cifra_core import Cifra


def test_cifra_key_round_trips():
    c = Cifra(artist="Djavan", name="Sina", cifra=("A  D/A",), key="A")
    assert c.key == "A"
    assert c.to_dict()["key"] == "A"
    assert Cifra.from_api(c.to_dict()) == c


def test_cifra_key_defaults_empty():
    assert Cifra(artist="x", name="y").key == ""
    assert Cifra.from_api({"artist": "x", "name": "y"}).key == ""
