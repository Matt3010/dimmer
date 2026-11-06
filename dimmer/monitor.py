"""I monitor via DDC/CI. Il DDC/CI è lento (decine di ms a comando): le scritture le fa
un thread a parte e, se intanto arrivano più valori per lo stesso monitor, manda solo l'ultimo."""
import threading


class Monitor:
    def __init__(self, sbc=None):
        if sbc is None:
            import screen_brightness_control as sbc
        self._sbc = sbc
        self.nomi = list(sbc.list_monitors())
        self._da_applicare = {}
        self._lock = threading.Lock()
        self._evento = threading.Event()
        threading.Thread(target=self._lavora, daemon=True).start()

    def leggi(self):
        try:
            valori = list(self._sbc.get_brightness())
        except Exception:
            valori = []
        return (valori + [50] * len(self.nomi))[:len(self.nomi)]

    def imposta(self, indice, valore):
        with self._lock:
            self._da_applicare[indice] = int(valore)
        self._evento.set()

    def in_attesa(self):
        with self._lock:
            return bool(self._da_applicare)

    def _lavora(self):
        while True:
            self._evento.wait()
            self._evento.clear()
            with self._lock:
                lavori = dict(self._da_applicare)
            for indice, valore in lavori.items():
                try:
                    self._sbc.set_brightness(valore, display=indice)
                except Exception:
                    pass
            with self._lock:   # tolti solo se intanto non ne è arrivato uno nuovo
                for indice, valore in lavori.items():
                    if self._da_applicare.get(indice) == valore:
                        del self._da_applicare[indice]
