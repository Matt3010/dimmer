"""Rifà gli screenshot del README (docs/), in inglese e con dati di esempio.
Apre il pannello per qualche secondo; non tocca i monitor né la configurazione.
Uso: python strumenti/screenshot.py"""
import os
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

from PIL import Image, ImageDraw, ImageGrab  # noqa: E402

from dimmer import app as modulo_app, config, tema, win32  # noqa: E402

USCITA = os.path.join(RADICE, "docs")
PRESET = {"Work": {"monitor": 70, "filtro": 0}, "Movie": {"monitor": [35, 55], "filtro": 0},
          "Night": {"monitor": 0, "filtro": 30}, "Reading": {"monitor": 50, "filtro": 0}}


class MonitorEsempio:
    nomi = ["Acer E", "Acer H"]

    def leggi(self):
        return [70, 70]

    def imposta(self, i, v):
        pass

    def in_attesa(self):
        return False


class Evento:
    def __init__(self, x):
        self.x, self.y = x, 20


def ritaglia(win, nome):
    """Lo screenshot della finestra con gli angoli trasparenti (fuori dall'isola)."""
    win.update()
    x, y, w, h = win.winfo_rootx(), win.winfo_rooty(), win.winfo_width(), win.winfo_height()
    img = ImageGrab.grab((x, y, x + w, y + h), all_screens=True).convert("RGBA")
    s = tema.SS
    forma = Image.new("L", (w * s, h * s), 0)
    ImageDraw.Draw(forma).rounded_rectangle((0, 0, w * s - 1, h * s - 1), tema.R_LG * s, fill=255)
    img.putalpha(forma.resize((w, h), Image.LANCZOS))
    img.save(os.path.join(USCITA, nome + ".png"))


def main():
    os.makedirs(USCITA, exist_ok=True)
    win32.dpi_reale()
    win32.carica_font_privati(tema.FILE_FONT)
    cfg = config.Config.__new__(config.Config)
    cfg.dati = {"filtro": 0, "lingua": "en", "preset": {k: dict(v) for k, v in PRESET.items()}}
    cfg.salva = lambda: None
    app = modulo_app.App(monitor=MonitorEsempio(), config=cfg)
    p, root = app.pannello, app.root

    def monitor():
        p.scheda = 0
        p.mostra()
        root.after(300, scheda_monitor)

    def scheda_monitor():
        ritaglia(p.win, "displays")
        p.chiudi()
        p.scheda = 1
        root.after(300, preset)

    def preset():
        p.mostra()
        root.after(300, scheda_preset)

    def scheda_preset():
        r = p.righe["Movie"]
        r._muovi(Evento(r.W - 50), True)
        ritaglia(p.win, "presets")
        r._muovi(Evento(0), False)
        p.chiedi_nome()
        p.campo.entry.insert(0, "Gaming")
        ritaglia(p.win, "new-preset")
        p.chiudi()
        root.after(300, rotella)

    def rotella():
        app.applica(valori=[0, 0], filtro=30)
        app.osd.mostra(app.valori, app.filtro)
        root.after(300, lambda: (ritaglia(app.osd.win, "wheel"), app.applica(filtro=0), root.destroy()))

    root.after(400, monitor)
    root.mainloop()


if __name__ == "__main__":
    main()
