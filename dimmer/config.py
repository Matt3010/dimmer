"""Preset e oscuramento salvati in %APPDATA%\\Dimmer\\config.json."""
import json
import os

NOME_APP = "Dimmer"

PRESET_DEFAULT = {
    "Lavoro": {"monitor": 70, "filtro": 0},
    "Film": {"monitor": 40, "filtro": 0},
    "Notte": {"monitor": 0, "filtro": 40},
}


def file_config():
    return os.path.join(os.environ.get("APPDATA", "."), NOME_APP, "config.json")


class Config:
    def __init__(self, percorso=None):
        self.percorso = percorso or file_config()
        self.dati = self._carica()

    def _carica(self):
        try:
            with open(self.percorso, encoding="utf8") as f:
                dati = json.load(f)
        except (OSError, ValueError):
            dati = {}
        if not isinstance(dati, dict):
            dati = {}
        if not isinstance(dati.get("filtro"), int):
            dati["filtro"] = 0
        if not isinstance(dati.get("preset"), dict):
            dati["preset"] = None             # li crea assicura_preset, nella lingua scelta
        if dati.get("lingua") not in ("auto", "it", "en"):
            dati["lingua"] = "auto"
        return dati

    def assicura_preset(self, traduci=lambda nome: nome):
        """Solo la prima volta: i preset di fabbrica, coi nomi nella lingua dell'app.
        Quelli eliminati poi non tornano."""
        if self.dati["preset"] is None:
            self.dati["preset"] = {traduci(n): dict(p) for n, p in PRESET_DEFAULT.items()}

    @property
    def preset(self):
        return self.dati["preset"]

    @property
    def lingua(self):
        return self.dati["lingua"]

    @lingua.setter
    def lingua(self, valore):
        self.dati["lingua"] = valore

    @property
    def filtro(self):
        return self.dati["filtro"]

    @filtro.setter
    def filtro(self, valore):
        self.dati["filtro"] = valore

    def salva(self):
        """Scrive su un file accanto e poi lo sostituisce: mai una config a metà."""
        os.makedirs(os.path.dirname(self.percorso), exist_ok=True)
        temporaneo = self.percorso + ".tmp"
        with open(temporaneo, "w", encoding="utf8") as f:
            json.dump(self.dati, f, indent=2, ensure_ascii=False)
        os.replace(temporaneo, self.percorso)
