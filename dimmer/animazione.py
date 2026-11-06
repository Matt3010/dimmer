"""Entrate e uscite alla Windows 11: curve Fluent, un fotogramma per refresh dello schermo."""
import time
import tkinter as tk

from . import win32
from .tema import TRASPARENTE

ENTRATA_PX, ENTRATA_S, USCITA_S = 40, 0.30, 0.16


def bezier(x1, y1, x2, y2):
    """Curva cubic-bezier come in CSS: dato il tempo (0..1) restituisce l'avanzamento."""
    def curva(t):
        lo, hi = 0.0, 1.0
        for _ in range(24):
            u = (lo + hi) / 2
            if 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u ** 2 * x2 + u ** 3 < t:
                lo = u
            else:
                hi = u
        u = (lo + hi) / 2
        return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3
    return curva


DECELERA = bezier(0.1, 0.9, 0.2, 1.0)   # Fluent "decelerate": per entrare
ACCELERA = bezier(0.7, 0.0, 1.0, 0.5)   # Fluent "accelerate": per uscire


class Animazione:
    """Sposta in verticale e dissolve una finestra: posizione e opacità cambiano insieme
    (direttamente con le API, non con due comandi Tk separati) e ogni fotogramma aspetta
    il refresh dello schermo. Finisce prima di tornare (300 ms al massimo): intanto
    `in_corso` dice al resto dell'app di aspettare."""
    in_corso = False
    _chiave = win32.colorref(TRASPARENTE)

    def __init__(self, win):
        self.win = win

    def avvia(self, x, y0, y1, a0, a1, durata, curva, fine=None, anticipo_alpha=1.0):
        w = self.win
        try:
            w.attributes("-alpha", a0)
            w.geometry(f"+{x}+{y0}")
            Animazione.in_corso = True
            w.update()                    # contenuto già disegnato prima del primo fotogramma
            h = win32.hwnd(w)
        except tk.TclError:
            Animazione.in_corso = False
            return
        inizio = time.perf_counter()
        while True:
            t = min(1.0, (time.perf_counter() - inizio) / durata)
            alpha = a0 + (a1 - a0) * min(1.0, t / anticipo_alpha)
            win32.sposta_e_dissolvi(h, x, round(y0 + (y1 - y0) * curva(t)), alpha, self._chiave)
            win32.aspetta_fotogramma()
            if t >= 1:
                break
        Animazione.in_corso = False
        try:
            w.attributes("-alpha", a1)    # Tk torna d'accordo con lo stato finale
            w.geometry(f"+{x}+{y1}")
        except tk.TclError:
            return
        if fine:
            fine()
