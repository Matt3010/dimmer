"""Italiano e inglese, a mano: il testo italiano è la chiave, qui sotto la traduzione.
Un test fallisce se una frase passata a t() non ha la sua traduzione."""
import ctypes

INGLESE = {
    # pannello
    "Monitor": "Displays",
    "Preset": "Presets",
    "Tutti": "All",
    "Oscuramento": "Dimming",
    "Spento": "Off",
    "Nessun preset: creane uno con i valori attuali.": "No presets yet: create one from the current values.",
    "Nuovo preset": "New preset",
    "Prende i valori attuali": "Uses the current values",
    "Crea": "Create",
    "Annulla": "Cancel",
    "Creato con i valori attuali": "Created with the current values",
    "Aggiornato con i valori attuali": "Updated with the current values",
    "Tocca ancora per eliminare": "Click again to delete",
    # descrizioni dei preset e suggerimento dell'icona
    "oscuramento": "dimming",
    "osc.": "dim.",
    # indicatore della rotellina
    "Luminosità": "Brightness",
    # menu della tray
    "Avvia con Windows": "Start with Windows",
    "Lingua": "Language",
    "Automatica": "Automatic",
    "Esci": "Quit",
    # i nomi dei preset di fabbrica (poi sono dati tuoi e restano come sono)
    "Lavoro": "Work",
    "Film": "Movie",
    "Notte": "Night",
}

SCELTE = ("auto", "it", "en")      # "auto" segue la lingua di Windows
NOMI_LINGUE = {"it": "Italiano", "en": "English"}   # ognuna nella sua lingua: non si traducono

_attuale = "it"


def lingua_di_sistema():
    """Italiano se Windows è in italiano, altrimenti inglese."""
    try:
        lingua = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except Exception:
        return "it"
    return "it" if lingua & 0x3FF == 0x10 else "en"   # 0x10 = LANG_ITALIAN


def imposta(scelta):
    global _attuale
    _attuale = scelta if scelta in NOMI_LINGUE else lingua_di_sistema()


def attuale():
    return _attuale


def t(testo):
    return INGLESE.get(testo, testo) if _attuale == "en" else testo
