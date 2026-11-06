"""I controlli del pannello, disegnati con Pillow sopra un Canvas."""
import time
import tkinter as tk
import tkinter.font as tkfont

from PIL import Image, ImageDraw, ImageTk

from .animazione import DECELERA
from .grafica import gradiente, gradiente_v, icona_foto, icona_larghezza, manopola, mescola, rettangolo
from .logica import PASSO_ROTELLA
from .lingua import t
from .tema import (BASE, BENE, ENTRA, F_CAMPO, F_CHIP, F_HINT, F_LABEL, F_TASTO_PRIMARIO, HAIRLINE,
                   ICONA_CESTINO, ICONA_OK, ICONA_SALVA, INK, INK_2, INK_3, ON_ACCENT, PERICOLO,
                   R_FLAT, R_IN, SS, SUNKEN, SUNKEN_HOVER)


def _tela(parent, w, h, mano=True):
    return dict(master=parent, width=w, height=h, bg=BASE, highlightthickness=0, bd=0,
                cursor="hand2" if mano else "")


class Cursore(tk.Canvas):
    """Slider: binario «sunken», riempimento sfumato, manopola alla Windows 11."""
    H, M = 24, 11

    def __init__(self, parent, massimo, colori, al_cambio, larghezza):
        super().__init__(**_tela(parent, larghezza, self.H))
        self.L, self.massimo, self.al_cambio, self.colori = larghezza, massimo, al_cambio, colori
        self.sfumatura = gradiente(larghezza * SS, self.H * SS, *colori)
        self.valore, self.hover, self.premuto = 0, False, False
        self.item = self.create_image(0, 0, anchor="nw")
        self.bind("<Button-1>", self._clic)
        self.bind("<B1-Motion>", self._clic)
        self.bind("<ButtonRelease-1>", self._rilascio)
        self.bind("<MouseWheel>", self._rotella)
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<Configure>", self._ridimensiona)
        self.disegna()

    def _ridimensiona(self, e):
        if e.width != self.L:          # occupa tutta la larghezza della colonna
            self.L = e.width
            self.sfumatura = gradiente(self.L * SS, self.H * SS, *self.colori)
            self.disegna()

    def imposta(self, v):
        if v != self.valore:
            self.valore = v
            self.disegna()

    def _clic(self, e):
        self.premuto = True
        f = (e.x - self.M) / (self.L - 2 * self.M)
        self._cambia(round(max(0.0, min(1.0, f)) * self.massimo))

    def _rilascio(self, _):
        self.premuto = False
        self.disegna()

    def _rotella(self, e):
        passo = PASSO_ROTELLA if e.delta > 0 else -PASSO_ROTELLA
        self._cambia(max(0, min(self.massimo, self.valore + passo)))

    def _hover(self, h):
        self.hover = h
        self.disegna()

    def _cambia(self, v):
        cambiato = v != self.valore
        self.valore = v
        self.disegna()
        if cambiato:
            self.al_cambio(v)

    def disegna(self):
        s, L, H, M = SS, self.L, self.H, self.M
        img = Image.new("RGB", (L * s, H * s), BASE)
        cy, sp = H / 2, 4
        x = M + (L - 2 * M) * self.valore / self.massimo
        ImageDraw.Draw(img).rounded_rectangle(
            (M * s, (cy - sp / 2) * s, (L - M) * s, (cy + sp / 2) * s), sp / 2 * s, fill=SUNKEN_HOVER)
        if self.valore > 0:
            maschera = Image.new("L", img.size, 0)
            ImageDraw.Draw(maschera).rounded_rectangle(
                (M * s, (cy - sp / 2) * s, max(M + sp, x) * s, (cy + sp / 2) * s), sp / 2 * s, fill=255)
            img.paste(self.sfumatura, (0, 0), maschera)
        stato = "premuto" if self.premuto else ("hover" if self.hover else "")
        sprite = manopola(self.colori[1], stato)
        img.paste(sprite, (round(x * s - sprite.width / 2), round(cy * s - sprite.height / 2)), sprite)
        self.foto = ImageTk.PhotoImage(img.resize((L, H), Image.LANCZOS))
        self.itemconfig(self.item, image=self.foto)


class Schede(tk.Canvas):
    """Controllo a segmenti: l'indicatore scorre verso la scheda scelta (curva Fluent)."""
    H = 32

    def __init__(self, parent, voci, al_cambio, larghezza, scelta=0):
        super().__init__(**_tela(parent, larghezza, self.H))
        self.voci, self.W, self.scelta, self.pos = voci, larghezza, scelta, float(scelta)
        self.al_cambio, self.timer = al_cambio, None
        self.sw = (larghezza - 6) / len(voci)
        self.sfondo = self.create_image(0, 0, anchor="nw")
        self.testi = [self.create_text(3 + self.sw * (i + 0.5), self.H / 2, text=v, font=F_CHIP)
                      for i, v in enumerate(voci)]
        self.bind("<Button-1>", self._clic)
        self.disegna()

    def _clic(self, e):
        i = max(0, min(len(self.voci) - 1, int((e.x - 3) / self.sw)))
        if i == self.scelta:
            return
        self.scelta = i
        partenza, inizio = self.pos, time.perf_counter()

        def passo():
            t = min(1.0, (time.perf_counter() - inizio) / 0.22)
            self.pos = partenza + (i - partenza) * DECELERA(t)
            self.disegna()
            self.timer = self.after(8, passo) if t < 1 else None
        if self.timer:
            self.after_cancel(self.timer)
        passo()
        self.al_cambio(i)

    def disegna(self):
        s, W, H = SS, self.W, self.H
        img = Image.new("RGB", (W * s, H * s), BASE)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0, 0, W * s - 1, H * s - 1), 10 * s, fill=SUNKEN)
        x = 3 + self.pos * self.sw
        d.rounded_rectangle((x * s, 3 * s, (x + self.sw) * s, (H - 3) * s), 8 * s,
                            fill=mescola(BASE, INK, 0.13))
        self.foto = ImageTk.PhotoImage(img.resize((W, H), Image.LANCZOS))
        self.itemconfig(self.sfondo, image=self.foto)
        for i, voce in enumerate(self.testi):
            self.itemconfig(voce, fill=INK if i == self.scelta else INK_2)


class RigaPreset(tk.Canvas):
    """Una riga dell'elenco preset: clic = applica; col mouse sopra, salva e cestino
    (il cestino chiede conferma con un secondo clic)."""
    H = 46

    def __init__(self, parent, nome, icona, larghezza, al_clic, al_salva, al_elimina):
        super().__init__(**_tela(parent, larghezza, self.H))
        self.W, self.nome, self.icona = larghezza, nome, icona
        self.sottotitolo, self.attivo, self.hover = "", False, False
        self.sopra, self.conferma, self.messaggio = None, False, None
        self.azioni = {"applica": al_clic, "salva": al_salva, "elimina": al_elimina}
        self.sfondo = self.create_image(0, 0, anchor="nw")
        self.t_icona = self.create_image(ENTRA + 15, self.H / 2)
        self.t_nome = self.create_text(ENTRA + 40, 15, anchor="w", font=F_LABEL, text=nome, fill=INK)
        self.t_sotto = self.create_text(ENTRA + 40, 31, anchor="w", font=F_HINT)
        # i tasti finiscono sul margine destro del testo (W - ENTRA), come il resto del pannello
        self.cx_elimina, self.cx_salva = self.W - ENTRA - 13, self.W - ENTRA - 43
        self.spazio_testo = self.cx_salva - 15 - 6 - (ENTRA + 40)   # fino ai tasti, con 6px d'aria
        self.t_salva = self.create_image(self.cx_salva, self.H / 2)
        self.t_elimina = self.create_image(self.cx_elimina, self.H / 2)
        self.bind("<Enter>", lambda e: self._muovi(e, True))
        self.bind("<Motion>", lambda e: self._muovi(e, True))
        self.bind("<Leave>", lambda e: self._muovi(e, False))
        self.bind("<Button-1>", self._clic)
        self.disegna()

    def _zona(self, x):
        if x >= self.cx_elimina - 15:
            return "elimina"
        if x >= self.cx_salva - 15:
            return "salva"
        return None

    def _muovi(self, e, dentro):
        sopra = self._zona(e.x) if dentro else None
        if not dentro:
            self.conferma = False
        if (dentro, sopra) != (self.hover, self.sopra):
            self.hover, self.sopra = dentro, sopra
            self.disegna()

    def _clic(self, e):
        zona = self._zona(e.x)
        if zona == "elimina":
            if self.conferma:
                self.azioni["elimina"]()
                return
            self.conferma = True
            self.disegna()
            self.after(2500, lambda: self.winfo_exists() and self._annulla_conferma())
        elif zona == "salva":
            self.azioni["salva"]()
        else:
            self.azioni["applica"]()

    def _annulla_conferma(self):
        self.conferma = False
        self.disegna()

    def imposta(self, sottotitolo, attivo):
        if (sottotitolo, attivo) != (self.sottotitolo, self.attivo):
            self.sottotitolo, self.attivo = sottotitolo, attivo
            self.disegna()

    def lampeggia(self, testo):
        self.messaggio = testo
        self.disegna()

        def fine():
            if self.winfo_exists():
                self.messaggio = None
                self.disegna()
        self.after(1300, fine)

    def disegna(self):
        s, W, H = SS, self.W, self.H
        img = Image.new("RGB", (W * s, H * s), BASE)
        d = ImageDraw.Draw(img)
        if self.hover or self.attivo:
            d.rounded_rectangle((0, 0, W * s - 1, H * s - 1), R_FLAT * s,
                                fill=SUNKEN if self.hover else mescola(BASE, INK, 0.05))
        quadro = mescola(BASE, INK, 0.13) if self.attivo else (SUNKEN_HOVER if self.hover else SUNKEN)
        d.rounded_rectangle((ENTRA * s, 8 * s, (ENTRA + 30) * s, 38 * s), 10 * s, fill=quadro)
        if self.hover:
            for zona, cx in (("salva", self.cx_salva), ("elimina", self.cx_elimina)):
                rosso = zona == "elimina" and self.conferma
                if self.sopra == zona or rosso:
                    d.rounded_rectangle(((cx - 13) * s, (H / 2 - 13) * s, (cx + 13) * s, (H / 2 + 13) * s),
                                        R_IN * s, fill=mescola(BASE, PERICOLO, 0.2) if rosso else SUNKEN_HOVER)
        self.foto = ImageTk.PhotoImage(img.resize((W, H), Image.LANCZOS))
        self.itemconfig(self.sfondo, image=self.foto)
        self.itemconfig(self.t_icona, image=icona_foto(self.icona, 14, INK if self.attivo else INK_2))
        if self.conferma:
            sotto, colore = t("Tocca ancora per eliminare"), PERICOLO
        elif self.messaggio:
            sotto, colore = self.messaggio, BENE
        else:
            sotto, colore = self.sottotitolo, INK_3
        self.itemconfig(self.t_sotto, text=sotto, fill=colore)
        if self.hover:
            self.coords(self.t_elimina, self.cx_elimina, H / 2)
            self.itemconfig(self.t_salva, image=icona_foto(
                ICONA_SALVA, 14, INK if self.sopra == "salva" else INK_2))
            self.itemconfig(self.t_elimina, image=icona_foto(
                ICONA_CESTINO, 14, PERICOLO if self.conferma else (INK if self.sopra == "elimina" else INK_2)))
        else:
            self.itemconfig(self.t_salva, image="")
            # la spunta tocca il margine destro, allineata alla percentuale in alto
            self.coords(self.t_elimina, W - ENTRA - icona_larghezza(ICONA_OK, 14) / 2, H / 2)
            self.itemconfig(self.t_elimina, image=icona_foto(ICONA_OK, 14, INK) if self.attivo else "")


class Tasto(tk.Canvas):
    """I tasti di SendLater, misura piccola: «ghost» (bordo hairline) e «primario» (pieno chiaro)."""
    H = 30

    def __init__(self, parent, testo, al_clic, tipo="ghost", icona=None, larghezza=None):
        self.tipo, self.icona, self.hover = tipo, icona, False
        font = F_TASTO_PRIMARIO if tipo == "primario" else F_CHIP
        li, spazio = (14, 6) if icona else (0, 0)
        lt = tkfont.Font(font=font).measure(testo)
        W = larghezza or (lt + li + spazio + 24)
        super().__init__(**_tela(parent, W, self.H))
        self.W = W
        x = (W - li - spazio - lt) / 2
        self.sfondo = self.create_image(0, 0, anchor="nw")
        self.t_i = self.create_image(x + li / 2, self.H / 2) if icona else None
        self.t_t = self.create_text(x + li + spazio, self.H / 2, anchor="w", font=font, text=testo)
        self.bind("<Button-1>", lambda e: al_clic())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.disegna()

    def _hover(self, h):
        self.hover = h
        self.disegna()

    def disegna(self):
        W, H = self.W, self.H
        if self.tipo == "primario":
            img = rettangolo(W, H, R_IN, BASE)
            maschera = rettangolo(W, H, R_IN, "#ffffff", sfondo="#000000").convert("L")
            img.paste(gradiente_v(W, H, "#ffffff", "#eef1f5" if self.hover else "#dfe4ea"), (0, 0), maschera)
            colore = ON_ACCENT
        else:
            img = rettangolo(W, H, R_IN, SUNKEN if self.hover else BASE, HAIRLINE)
            colore = INK if self.hover else INK_2
        self.foto = ImageTk.PhotoImage(img)
        self.itemconfig(self.sfondo, image=self.foto)
        self.itemconfig(self.t_t, fill=colore)
        if self.t_i:
            self.itemconfig(self.t_i, image=icona_foto(self.icona, 14, colore))


class Campo(tk.Canvas):
    """L'input di SendLater a fuoco: sfondo pieno, bordo accento 45%, anello di 3.5px all'11%.
    Largo `larghezza` più 4px per lato per l'anello."""
    H, A = 38, 4

    def __init__(self, parent, larghezza, al_invio, all_esc):
        W, H, A, s = larghezza, self.H, self.A, SS
        super().__init__(**_tela(parent, W + 2 * A, H + 2 * A, mano=False))
        img = Image.new("RGB", ((W + 2 * A) * s, (H + 2 * A) * s), BASE)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((0.5 * s, 0.5 * s, (W + 2 * A - 0.5) * s, (H + 2 * A - 0.5) * s),
                            (R_IN + 3.5) * s, fill=mescola(BASE, INK, 0.11))
        d.rounded_rectangle((A * s, A * s, (W + A) * s - 1, (H + A) * s - 1), R_IN * s,
                            fill=BASE, outline=mescola(BASE, INK, 0.45), width=s)
        self.foto = ImageTk.PhotoImage(img.resize((W + 2 * A, H + 2 * A), Image.LANCZOS))
        self.create_image(0, 0, anchor="nw", image=self.foto)
        self.entry = tk.Entry(self, bg=BASE, fg=INK, insertbackground=INK, relief="flat", bd=0,
                              highlightthickness=0, font=F_CAMPO)
        self.create_window(A + 11, A + H / 2, anchor="w", window=self.entry, width=W - 22)
        self.entry.bind("<Return>", lambda e: (al_invio(self.entry.get()), "break")[1])
        self.entry.bind("<Escape>", lambda e: (all_esc(), "break")[1])

    def fuoco(self):
        self.entry.focus_set()
