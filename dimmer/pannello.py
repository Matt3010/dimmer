"""Il pannello che si apre dall'icona: schede Monitor e Preset."""
import tkinter as tk
import tkinter.font as tkfont

from .animazione import ACCELERA, DECELERA, ENTRATA_PX, ENTRATA_S, USCITA_S, Animazione
from .finestre import Superficie
from .grafica import icona_foto
from .lingua import t
from .logica import MAX_FILTRO, descrivi_valori, media, pulisci_nome, valori_preset
from .tema import (ACCENTO, BASE, CARD_PAD, ENTRA, F_HINT, F_LABEL, F_TITOLO, F_VALORE, HAIRLINE,
                   ICONA_LUNA, ICONA_PIU, ICONA_SOLE, ICONA_STELLA, ICONE_PRESET, INK, INK_2, INK_3,
                   ME_CHIARO, NOTTE)
from .widget import Campo, Cursore, RigaPreset, Schede, Tasto


class Pannello:
    L = 280          # larghezza di partenza degli slider (poi si allargano)
    LP = 296         # larghezza della colonna

    def __init__(self, app):
        self.app = app
        self.win = None
        self.anim = None
        self.scheda = 0  # resta quella dell'ultima volta
        self._font_hint = None

    # ---------- apertura e chiusura ----------
    def mostra(self):
        if self.win is not None:
            self.chiudi()
            return
        app = self.app
        app.rileggi_monitor()        # i valori veri arrivano dopo: il pannello si apre subito
        self.sup = Superficie(app.root, pad_x=CARD_PAD - ENTRA)   # le righe entrano di ENTRA px
        w = self.win = self.sup.win
        w.attributes("-alpha", 0.0)
        self.anim = None             # finché è None, cambiare scheda non ridimensiona
        self.cursori, self.etichette, self.righe = {}, {}, {}
        corpo = self.sup.corpo

        testa = tk.Frame(corpo, bg=BASE)
        testa.pack(fill="x", pady=(0, 10), padx=ENTRA)
        self.icona_testa = tk.Label(testa, bg=BASE, bd=0)
        self.icona_testa.pack(side="left")
        tk.Label(testa, text="Dimmer", font=F_TITOLO, bg=BASE, fg=INK).pack(side="left", padx=(8, 0))
        self.valore_testa = tk.Label(testa, font=F_VALORE, bg=BASE, fg=INK_2)
        self.valore_testa.pack(side="right")
        Schede(corpo, [t("Monitor"), t("Preset")], self.vai_scheda, self.LP, self.scheda).pack(pady=(0, 10), padx=ENTRA)
        tk.Frame(corpo, bg=BASE, width=self.LP, height=0).pack(padx=ENTRA)   # larghezza fissa della colonna

        self.pag_monitor = tk.Frame(corpo, bg=BASE)
        self._costruisci_monitor(self.pag_monitor)
        self.pag_preset = tk.Frame(corpo, bg=BASE)
        self.lista = tk.Frame(self.pag_preset, bg=BASE)
        self.lista.pack(fill="x")
        self.fondo_preset = tk.Frame(self.pag_preset, bg=BASE)
        self.fondo_preset.pack(fill="x", pady=(8, 0), padx=ENTRA - Campo.A)   # spazio per l'anello del campo
        self.costruisci_lista()
        self.tasto_nuovo()

        self.vai_scheda(self.scheda)
        self.sincronizza()
        self.sup.in_basso_a_destra(alzato=ENTRATA_PX)
        self.anim = Animazione(w)
        w.bind("<FocusOut>", lambda e: app.root.after(150, self._forse_chiudi))
        w.bind("<Escape>", lambda e: self.chiudi())
        w.lift()
        w.focus_force()
        self.anim.avvia(self.sup.x, self.sup.y + ENTRATA_PX, self.sup.y, 0.0, 1.0,
                        ENTRATA_S, DECELERA, anticipo_alpha=0.4)

    def _forse_chiudi(self):
        if self.win is not None and self.win.focus_get() is None:
            self.chiudi()

    def chiudi(self):
        """Esce come i pannelli di Windows 11: scende accelerando e sparisce."""
        if self.win is None:
            return
        win, self.win = self.win, None
        y = win.winfo_rooty()
        self.anim.avvia(self.sup.x, y, y + ENTRATA_PX, float(win.attributes("-alpha")), 0.0,
                        USCITA_S, ACCELERA, fine=win.destroy)

    def vai_scheda(self, i):
        self.scheda = i
        self.pag_monitor.pack_forget()
        self.pag_preset.pack_forget()
        if i == 0:
            self.pag_monitor.pack(fill="x", padx=ENTRA)
        else:
            self.pag_preset.pack(fill="x")
        if self.anim is not None:
            self._ridimensiona()

    def _ridimensiona(self):
        self.win.attributes("-alpha", 1.0)
        self.sup.in_basso_a_destra()

    # ---------- scheda Monitor ----------
    def _costruisci_monitor(self, p):
        app = self.app
        self._riga(p, "tutti", t("Tutti"), 100, ACCENTO,
                   lambda v: v != self.tutti_mostrato and app.applica(valori=[v] * len(app.nomi)),
                   forte=True, primo=True)
        for i, nome in enumerate(app.nomi):
            self._riga(p, i, nome, 100, ACCENTO, lambda v, i=i: self._cambia_monitor(i, v))
        tk.Frame(p, bg=HAIRLINE, height=1).pack(fill="x", pady=10)
        self._riga(p, "filtro", t("Oscuramento"), MAX_FILTRO, NOTTE,
                   lambda v: v != app.filtro and app.applica(filtro=v), forte=True, primo=True)

    def _riga(self, parent, chiave, nome, massimo, colori, al_cambio, forte=False, primo=False):
        su = tk.Frame(parent, bg=BASE)
        su.pack(fill="x", pady=(0 if primo else 2, 0))
        tk.Label(su, text=nome, font=F_LABEL, bg=BASE, fg=INK if forte else INK_2,
                 bd=0, padx=0, pady=0).pack(side="left")
        # come Twinkle Tray: il valore sta accanto allo slider, in una colonna di larghezza fissa
        giu = tk.Frame(parent, bg=BASE)
        giu.pack(fill="x")
        self.etichette[chiave] = tk.Label(giu, font=F_VALORE, bg=BASE, fg=INK if forte else INK_2,
                                          width=6, anchor="e", bd=0, padx=0, pady=0)
        self.etichette[chiave].pack(side="right")
        self.cursori[chiave] = Cursore(giu, massimo, colori, al_cambio, self.L - 44)
        self.cursori[chiave].pack(side="left", fill="x", expand=True)

    def _cambia_monitor(self, i, v):
        if v != self.app.valori[i]:
            nuovi = list(self.app.valori)
            nuovi[i] = v
            self.app.applica(valori=nuovi)

    def sincronizza(self):
        """Porta slider ed elenco allo stato dell'app, senza rimandare comandi ai monitor."""
        if self.win is None:
            return
        app = self.app
        self.tutti_mostrato = media(app.valori)
        self.cursori["tutti"].imposta(self.tutti_mostrato)
        self.etichette["tutti"].config(text=f"{self.tutti_mostrato}%")
        for i, v in enumerate(app.valori):
            self.cursori[i].imposta(v)
            self.etichette[i].config(text=f"{v}%")
        self.cursori["filtro"].imposta(app.filtro)
        self.etichette["filtro"].config(text=f"{app.filtro}%" if app.filtro else t("Spento"))
        if app.filtro:
            self.icona_testa.config(image=icona_foto(ICONA_LUNA, 16, ME_CHIARO))
            self.valore_testa.config(text=f"−{app.filtro}%")
        else:
            self.icona_testa.config(image=icona_foto(ICONA_SOLE, 16, INK))
            self.valore_testa.config(text=f"{self.tutti_mostrato}%")
        attuale = (list(app.valori), app.filtro)
        for nome, riga in self.righe.items():
            valori, filtro = valori_preset(app.cfg.preset[nome], len(app.nomi))
            testo = descrivi_valori(app.nomi, valori, filtro,
                                    entra=lambda t, r=riga: self._misura(t) <= r.spazio_testo)
            riga.imposta(testo, (valori, filtro) == attuale)

    def _misura(self, testo):
        if self._font_hint is None:
            self._font_hint = tkfont.Font(font=F_HINT)
        return self._font_hint.measure(testo)

    # ---------- scheda Preset ----------
    def costruisci_lista(self):
        for f in self.lista.winfo_children():
            f.destroy()
        self.righe = {}
        app = self.app
        for nome in app.cfg.preset:
            r = RigaPreset(self.lista, nome, ICONE_PRESET.get(nome, ICONA_STELLA), self.LP + 2 * ENTRA,
                           lambda n=nome: app.applica_preset(n),
                           lambda n=nome: self._sovrascrivi(n),
                           lambda n=nome: self._elimina(n))
            r.pack(pady=(0, 2))
            self.righe[nome] = r
        if not self.righe:
            tk.Label(self.lista, text=t("Nessun preset: creane uno con i valori attuali."),
                     font=F_HINT, bg=BASE, fg=INK_3, wraplength=self.LP, justify="left").pack(anchor="w", pady=(2, 4), padx=ENTRA)

    def _sovrascrivi(self, nome):
        self.app.salva_preset(nome)
        self.sincronizza()
        self.righe[nome].lampeggia(t("Aggiornato con i valori attuali"))

    def _elimina(self, nome):
        self.app.elimina_preset(nome)
        self.costruisci_lista()
        self.sincronizza()
        self._ridimensiona()

    def _svuota_fondo(self):
        for f in self.fondo_preset.winfo_children():
            f.destroy()

    def tasto_nuovo(self):
        self._svuota_fondo()
        Tasto(self.fondo_preset, t("Nuovo preset"), self.chiedi_nome, icona=ICONA_PIU,
              larghezza=self.LP).pack(padx=Campo.A)
        self.campo = None

    def chiedi_nome(self):
        self._svuota_fondo()

        def annulla():
            self.tasto_nuovo()
            self._ridimensiona()

        self.campo = Campo(self.fondo_preset, self.LP, self._crea, annulla)
        self.campo.pack()
        riga = tk.Frame(self.fondo_preset, bg=BASE)
        riga.pack(fill="x", padx=Campo.A, pady=(6, 0))
        tk.Label(riga, text=t("Prende i valori attuali"), font=F_HINT, bg=BASE, fg=INK_3).pack(side="left")
        Tasto(riga, t("Crea"), lambda: self._crea(self.campo.entry.get()), tipo="primario").pack(side="right")
        Tasto(riga, t("Annulla"), annulla).pack(side="right", padx=(0, 8))
        self.campo.fuoco()
        self._ridimensiona()

    def _crea(self, nome):
        nome = pulisci_nome(nome)
        if not nome:
            return
        self.app.salva_preset(nome)
        self.costruisci_lista()
        self.tasto_nuovo()
        self.sincronizza()
        self._ridimensiona()
        self.righe[nome].lampeggia(t("Creato con i valori attuali"))
