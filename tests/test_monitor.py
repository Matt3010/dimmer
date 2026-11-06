import threading
import time

from dimmer.monitor import Monitor


class SbcFinto:
    def __init__(self, valori=(40, 60), lento=0.0, rotto=False):
        self.valori, self.lento, self.rotto = list(valori), lento, rotto
        self.scritture = []
        self.prima = threading.Event()

    def list_monitors(self):
        return ["A", "B"]

    def get_brightness(self):
        if self.rotto:
            raise RuntimeError("DDC/CI spento")
        return list(self.valori)

    def set_brightness(self, valore, display):
        self.prima.set()
        time.sleep(self.lento)
        self.scritture.append((display, valore))


def aspetta(condizione, secondi=2.0):
    fine = time.time() + secondi
    while time.time() < fine:
        if condizione():
            return True
        time.sleep(0.01)
    return False


def test_lettura_e_ripiego_se_il_ddc_non_risponde():
    assert Monitor(SbcFinto()).leggi() == [40, 60]
    assert Monitor(SbcFinto(rotto=True)).leggi() == [50, 50]


def test_valori_ravvicinati_mandano_solo_l_ultimo():
    sbc = SbcFinto(lento=0.1)
    m = Monitor(sbc)
    m.imposta(0, 10)
    assert sbc.prima.wait(1)          # il primo è partito: ora il thread è occupato
    for v in (20, 30, 40):
        m.imposta(0, v)
    assert aspetta(lambda: not m.in_attesa())
    assert sbc.scritture == [(0, 10), (0, 40)]


def test_in_attesa_finche_non_e_scritto():
    sbc = SbcFinto(lento=0.1)
    m = Monitor(sbc)
    m.imposta(1, 70)
    assert m.in_attesa()
    assert aspetta(lambda: not m.in_attesa())
    assert sbc.scritture == [(1, 70)]
