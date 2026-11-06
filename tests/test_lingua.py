import pathlib
import re

import pytest

from dimmer import lingua
from dimmer.config import PRESET_DEFAULT
from dimmer.logica import descrivi_valori, suggerimento_tray

SORGENTI = pathlib.Path(__file__).parent.parent / "dimmer"


@pytest.fixture(autouse=True)
def torna_all_italiano():
    yield
    lingua.imposta("it")


def frasi_tradotte_nel_codice():
    frasi = set()
    for f in SORGENTI.glob("*.py"):
        frasi |= set(re.findall(r'\bt\("((?:[^"\\]|\\.)*)"\)', f.read_text(encoding="utf8")))
    return frasi


def test_ogni_frase_ha_la_traduzione_inglese():
    frasi = frasi_tradotte_nel_codice()
    assert frasi, "nessuna chiamata a t() trovata: il test non guarderebbe niente"
    mancanti = sorted(f for f in frasi if f not in lingua.INGLESE)
    assert not mancanti, f"senza traduzione inglese: {mancanti}"
    assert set(PRESET_DEFAULT) <= set(lingua.INGLESE), "i preset di fabbrica vanno tradotti"


def test_nessuna_traduzione_dimenticata_nel_dizionario():
    usate = frasi_tradotte_nel_codice() | set(PRESET_DEFAULT)   # i nomi di fabbrica passano da t() così
    in_piu = sorted(set(lingua.INGLESE) - usate)
    assert not in_piu, f"traduzioni che il codice non usa più: {in_piu}"


def test_scelta_esplicita_e_automatica(monkeypatch):
    lingua.imposta("en")
    assert lingua.t("Esci") == "Quit"
    lingua.imposta("it")
    assert lingua.t("Esci") == "Esci"
    monkeypatch.setattr(lingua, "lingua_di_sistema", lambda: "en")
    lingua.imposta("auto")
    assert lingua.attuale() == "en"
    lingua.imposta("klingon")
    assert lingua.attuale() == "en"


def test_frase_sconosciuta_resta_com_e():
    lingua.imposta("en")
    assert lingua.t("Acer E") == "Acer E"


def test_descrizioni_in_inglese():
    lingua.imposta("en")
    assert descrivi_valori(["A", "B"], [0, 0], 10) == "All 0% · dimming 10%"
    assert suggerimento_tray(["A"], [5], 3) == "A 5% · dimming 3%"
