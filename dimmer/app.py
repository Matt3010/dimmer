"""L'applicazione: tiene lo stato (luminosità e oscuramento), l'icona nella tray e
smista i comandi che arrivano dagli altri thread (tray, rotellina, letture DDC)."""
import logging
import logging.handlers
import os
import queue
import sys
import threading
import tkinter as tk

import pystray

from . import win32
from . import lingua
from .animazione import Animazione
from . import __version__
from .config import NOME_APP, Config, file_config
from .finestre import Osd, Velo
from .grafica import icona_tray
from .lingua import t
from .logica import PASSO_ROTELLA, media, passo_rotella, suggerimento_tray, valori_preset
from .monitor import Monitor
from .pannello import Pannello
from .tema import FILE_FONT

GIRO_MS = 50                  # ogni quanto il thread Tk guarda la coda dei comandi
CONTROLLI_OGNI = 20           # giri: ~1 s per riposizionare velo e area dell'icona


class App:
    def __init__(self, monitor=None, config=None, script=None):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.report_callback_exception = lambda *e: log.error("errore nell'interfaccia", exc_info=e)
        self.monitor = monitor or Monitor()
        self.cfg = config or Config()
        lingua.imposta(self.cfg.lingua)
        self.cfg.assicura_preset(t)
        self.script = script
        self.nomi = self.monitor.nomi
        self.valori = self.monitor.leggi()
        log.info("monitor: %s, luminosità: %s", self.nomi or "nessuno", self.valori)
        self.filtro = 0
        self.comandi = queue.Queue()          # dagli altri thread al thread Tk
        self._timer_salva = None
        self._giri = 0
        self._icona_attuale = None
        self.velo = Velo(self.root)
        self.osd = Osd(self.root)
        self.pannello = Pannello(self)
        self.icona = pystray.Icon(NOME_APP, icona_tray(media(self.valori), False), NOME_APP, self._menu())
        self.hook = None
        self.applica(filtro=self.cfg.filtro)

    def _menu(self):
        def comando(c):
            return lambda icon, item: self.comandi.put(c)

        def voci_preset():                    # rilette a ogni apertura del menu
            return [pystray.MenuItem(n, comando(("preset", n))) for n in self.cfg.preset]

        def voce_lingua(scelta):
            nome = lingua.NOMI_LINGUE.get(scelta)
            return pystray.MenuItem(lambda item: nome or t("Automatica"), comando(("lingua", scelta)),
                                    checked=lambda item: self.cfg.lingua == scelta, radio=True)

        return pystray.Menu(            # testi come funzioni: seguono la lingua attuale
            pystray.MenuItem(f"{NOME_APP}…", comando("mostra"), default=True),
            pystray.MenuItem(lambda item: t("Preset"), pystray.Menu(voci_preset)),
            pystray.MenuItem(lambda item: t("Lingua"), pystray.Menu(*map(voce_lingua, lingua.SCELTE))),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: t("Avvia con Windows"), self._cambia_avvio,
                             checked=lambda item: win32.avvio_attivo(NOME_APP), enabled=bool(self.script)),
            pystray.MenuItem(lambda item: t("Esci"), comando("esci")),
        )

    def cambia_lingua(self, scelta):
        self.cfg.lingua = scelta
        self.cfg.salva()
        lingua.imposta(scelta)
        self.pannello.chiudi()          # alla prossima apertura è già nella lingua nuova
        self._icona_attuale = None      # anche il suggerimento sull'icona
        self._aggiorna_icona()
        self.icona.update_menu()

    def _cambia_avvio(self, icon, item):
        attivo = win32.avvio_attivo(NOME_APP)
        win32.imposta_avvio(NOME_APP, None if attivo else win32.comando_avvio(self.script))
        icon.update_menu()

    # ---------- stato ----------
    def applica(self, valori=None, filtro=None, osd=False):
        """L'unico punto che cambia luminosità e oscuramento: monitor, velo, icona, pannello."""
        if valori is not None:
            for i, (vecchio, nuovo) in enumerate(zip(self.valori, valori)):
                if vecchio != nuovo:
                    self.monitor.imposta(i, nuovo)
            self.valori = list(valori)
        if filtro is not None and filtro != self.filtro:
            self.filtro = filtro
            self.velo.imposta(filtro)
            self.velo.in_cima(self._finestra_sopra())
            self.cfg.filtro = filtro
            self._salva_tra_poco()
        self._aggiorna_icona()
        self.pannello.sincronizza()
        if osd and self.pannello.win is None:
            self.osd.mostra(self.valori, self.filtro)

    def _aggiorna_icona(self):
        chiave = (media(self.valori), self.filtro > 0, tuple(self.valori), self.filtro)
        if chiave == self._icona_attuale:    # niente chiamate alla shell se non cambia niente
            return
        self._icona_attuale = chiave
        self.icona.icon = icona_tray(media(self.valori), self.filtro > 0)
        self.icona.title = suggerimento_tray(self.nomi, self.valori, self.filtro)

    def _salva_tra_poco(self):
        """Mentre si trascina lo slider dell'oscuramento si salva una volta sola, alla fine."""
        if self._timer_salva:
            self.root.after_cancel(self._timer_salva)
        self._timer_salva = self.root.after(1000, self.cfg.salva)

    def applica_preset(self, nome):
        valori, filtro = valori_preset(self.cfg.preset[nome], len(self.nomi))
        self.applica(valori=valori, filtro=filtro, osd=True)

    def salva_preset(self, nome):
        self.cfg.preset[nome] = {"monitor": list(self.valori), "filtro": self.filtro}
        self._preset_cambiati()

    def elimina_preset(self, nome):
        self.cfg.preset.pop(nome, None)
        self._preset_cambiati()

    def _preset_cambiati(self):
        self.cfg.salva()
        self.icona.update_menu()

    def rileggi_monitor(self):
        """Rilegge i monitor in background (magari li hai cambiati coi loro tasti)."""
        threading.Thread(target=lambda: self.comandi.put(("letti", self.monitor.leggi())),
                         daemon=True).start()

    # ---------- comandi dagli altri thread ----------
    def _ciclo(self):
        if Animazione.in_corso:              # i comandi aspettano la fine dell'animazione
            self.root.after(GIRO_MS, self._ciclo)
            return
        while True:
            try:
                c = self.comandi.get_nowait()
            except queue.Empty:
                break
            if c == "esci":
                self._esci()
                return
            self._esegui(c)
        self._giri += 1
        if self._giri % CONTROLLI_OGNI == 0:
            self._controlli_lenti()
        self.root.after(GIRO_MS, self._ciclo)

    def _esegui(self, c):
        if c == "mostra":
            self.pannello.mostra()
        elif c[0] == "rotella":
            valori, filtro = passo_rotella(self.valori, self.filtro, c[1] * PASSO_ROTELLA)
            self.applica(valori=valori, filtro=filtro, osd=True)
        elif c[0] == "lingua":
            self.cambia_lingua(c[1])
        elif c[0] == "preset" and c[1] in self.cfg.preset:
            self.applica_preset(c[1])
        elif c[0] == "letti" and not self.monitor.in_attesa() and c[1] != self.valori:
            self.valori = list(c[1])          # valori veri: nessun comando da rimandare
            self._aggiorna_icona()
            self.pannello.sincronizza()

    def _controlli_lenti(self):
        """Una volta al secondo: dove sta l'icona (per la rotellina) e velo sopra la barra."""
        if self.hook:
            self.hook.area = win32.rettangolo_icona_tray(self.icona)
        if self.velo.visibile:
            self.velo.in_cima(self._finestra_sopra())

    def _finestra_sopra(self):
        for w in (self.pannello.win, self.osd.win):
            if w is not None and w.winfo_viewable():
                return win32.hwnd(w)
        return None

    def _esci(self):
        if self._timer_salva:
            self.cfg.salva()
        self.icona.stop()
        self.root.destroy()

    def avvia(self):
        self.hook = win32.HookRotella(lambda verso: self.comandi.put(("rotella", verso)))
        self.icona.run_detached()
        self._ciclo()
        self.root.after(500, self._controlli_lenti)   # l'icona appare dopo un attimo
        self.root.mainloop()


log = logging.getLogger("dimmer")


def prepara_log():
    """Un exe senza console nasconde gli errori: finiscono in %APPDATA%\\Dimmer\\dimmer.log
    (al massimo 2 file da 200 KB)."""
    percorso = os.path.join(os.path.dirname(file_config()), "dimmer.log")
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    gestore = logging.handlers.RotatingFileHandler(percorso, maxBytes=200_000, backupCount=1, encoding="utf8")
    gestore.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(gestore)
    log.setLevel(logging.INFO)
    sys.excepthook = lambda *e: log.critical("errore non gestito", exc_info=e)


def main(script):
    if not win32.unica_istanza(NOME_APP):   # già aperto: niente seconda icona
        return
    prepara_log()
    log.info("Dimmer %s avviato (%s)", __version__, "exe" if getattr(sys, "frozen", False) else "python")
    win32.dpi_reale()
    win32.carica_font_privati(FILE_FONT)
    app = App(script=script)
    if win32.avvio_attivo(NOME_APP):    # se la cartella si è spostata, il percorso resta giusto
        win32.imposta_avvio(NOME_APP, win32.comando_avvio(script))
    app.avvia()
