"""Le finestre: la superficie a isola (base di pannello e indicatore), il velo
dell'oscuramento e l'indicatore della rotellina."""
import tkinter as tk

from PIL import ImageTk

from . import win32
from .animazione import ACCELERA, DECELERA, ENTRATA_PX, ENTRATA_S, USCITA_S, Animazione
from .grafica import barra_piena, icona_foto, isola
from .logica import MAX_FILTRO, media
from .lingua import t
from .tema import (ACCENTO, BASE, CARD_PAD, F_TITOLO_P, F_VALORE, HAIRLINE, ICONA_LUNA, ICONA_SOLE,
                   INK, INK_2, NOTTE, R_LG, SUNKEN_HOVER, TRASPARENTE)

MARGINE = 12          # distanza dal bordo dello schermo e dalla barra


class Superficie:
    """Finestra a isola: angoli da 20px antialias (fuori sono trasparenti), bordo hairline,
    contenuto in `self.corpo`. `in_basso_a_destra()` la misura e la mette sopra la tray."""

    def __init__(self, root, pad_x=CARD_PAD):
        self.pad_x = pad_x
        w = self.win = tk.Toplevel(root, bg=TRASPARENTE)
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        w.attributes("-transparentcolor", TRASPARENTE)
        self.tela = tk.Canvas(w, bg=TRASPARENTE, highlightthickness=0, bd=0)
        self.tela.pack()
        self.corpo = tk.Frame(self.tela, bg=BASE)
        self.sfondo = self.tela.create_image(0, 0, anchor="nw")
        self.tela.create_window(pad_x, CARD_PAD, anchor="nw", window=self.corpo)
        self.misura = None
        self.x = self.y = 0

    def _monta(self):
        self.corpo.update_idletasks()
        W = self.corpo.winfo_reqwidth() + 2 * self.pad_x
        H = self.corpo.winfo_reqheight() + 2 * CARD_PAD
        if (W, H) != self.misura:     # lo sfondo si ridisegna solo se cambia misura
            self.misura = (W, H)
            self.tela.config(width=W, height=H)
            self.foto = ImageTk.PhotoImage(isola(W, H, R_LG, BASE, HAIRLINE, TRASPARENTE))
            self.tela.itemconfig(self.sfondo, image=self.foto)
        return W, H

    def in_basso_a_destra(self, alzato=0):
        W, H = self._monta()
        _, _, destra, basso = win32.area_lavoro()
        self.x, self.y = destra - W - MARGINE, basso - H - MARGINE
        self.win.geometry(f"+{self.x}+{self.y + alzato}")


class Velo:
    """Velo nero sopra tutti gli schermi, attraversabile dal mouse: l'oscuramento sotto lo 0%."""

    def __init__(self, root):
        w = self.win = tk.Toplevel(root, bg="black")
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        w.attributes("-alpha", 0.0)
        x, y, larghezza, altezza = win32.schermo_virtuale()
        # 1 px in meno in altezza: se copre tutto lo schermo Windows lo scambia
        # per un'app a schermo intero e attiva da solo il "Non disturbare".
        w.geometry(f"{larghezza}x{altezza - 1}+{x}+{y}")
        win32.stile_esteso(w, click_through=True)
        self.hwnd = win32.hwnd(w)
        w.withdraw()
        self.visibile = False

    def imposta(self, filtro):
        if filtro <= 0:
            if self.visibile:
                self.win.withdraw()
                self.visibile = False
            return
        self.win.attributes("-alpha", filtro / 100)
        if not self.visibile:
            self.win.deiconify()
            win32.stile_esteso(self.win, click_through=True)
            self.visibile = True

    def in_cima(self, sotto_a=None):
        """Sopra la barra delle applicazioni, ma sotto pannello/indicatore se aperti."""
        win32.metti_in_cima(self.hwnd, sotto_a)


class Osd(Superficie):
    """Indicatore che compare quando si usa la rotellina sull'icona."""
    LB = 220
    DURATA_MS = 1300

    def __init__(self, root):
        super().__init__(root)
        su = tk.Frame(self.corpo, bg=BASE)
        su.pack(fill="x")
        self.icona = tk.Label(su, bg=BASE, bd=0)
        self.icona.pack(side="left")
        self.titolo = tk.Label(su, font=F_TITOLO_P, bg=BASE, fg=INK)
        self.titolo.pack(side="left", padx=(8, 0))
        self.valore = tk.Label(su, font=F_VALORE, bg=BASE, fg=INK_2)
        self.valore.pack(side="right")
        self.barra = tk.Label(self.corpo, bg=BASE, bd=0)
        self.barra.pack(pady=(10, 0))
        win32.stile_esteso(self.win)
        self.win.withdraw()
        self.timer = None
        self.visibile = False
        self.anim = Animazione(self.win)

    def mostra(self, valori, filtro):
        if filtro:
            icona, titolo, v, f, col = ICONA_LUNA, t("Oscuramento"), filtro, filtro / MAX_FILTRO, NOTTE
        else:
            icona, titolo, v, f, col = ICONA_SOLE, t("Luminosità"), media(valori), media(valori) / 100, ACCENTO
        self.icona.config(image=icona_foto(icona, 16, INK))
        self.titolo.config(text=titolo)
        self.valore.config(text=f"{v}%")
        self.foto_barra = ImageTk.PhotoImage(barra_piena(self.LB, 4, f, col, SUNKEN_HOVER))
        self.barra.config(image=self.foto_barra)
        self.in_basso_a_destra()
        if not self.visibile:
            self.visibile = True
            self.win.attributes("-alpha", 0.0)
            self.win.deiconify()
            self.anim.avvia(self.x, self.y + ENTRATA_PX // 2, self.y, 0.0, 1.0,
                            ENTRATA_S, DECELERA, anticipo_alpha=0.5)
        else:
            self.win.attributes("-alpha", 1.0)
        self.win.lift()
        if self.timer:
            self.win.after_cancel(self.timer)
        self.timer = self.win.after(self.DURATA_MS, self.nascondi)

    def nascondi(self):
        self.timer = None

        def fine():
            self.win.withdraw()
            self.visibile = False
        self.anim.avvia(self.x, self.y, self.y + ENTRATA_PX // 2, 1.0, 0.0, USCITA_S, ACCELERA, fine)
