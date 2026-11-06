"""Le regole di Dimmer: niente Tk e niente Windows, così si provano da sole."""
from .lingua import t

MAX_FILTRO = 85          # oltre, lo schermo diventa praticamente nero
PASSO_ROTELLA = 5
LUNGHEZZA_NOME = 24


def passo_rotella(valori, filtro, passo):
    """Scendendo si abbassano i monitor; arrivati a 0 si scurisce col filtro.
    Salendo prima si toglie il filtro, poi si alzano i monitor."""
    if passo < 0:
        if any(v > 0 for v in valori):
            return [max(0, v + passo) for v in valori], filtro
        return list(valori), min(MAX_FILTRO, filtro - passo)
    if filtro > 0:
        return list(valori), max(0, filtro - passo)
    return [min(100, v + passo) for v in valori], filtro


def media(valori):
    return sum(valori) // max(1, len(valori))


def valori_preset(preset, quanti):
    """Un preset salva un numero (tutti uguali) o un valore per monitor: lo porta
    a `quanti` valori, ripetendo l'ultimo se nel frattempo è arrivato un monitor."""
    valori = preset["monitor"]
    if isinstance(valori, int):
        valori = [valori]
    valori = list(valori) or [0]
    return (valori + [valori[-1]] * quanti)[:quanti], preset.get("filtro", 0)


def nomi_brevi(nomi):
    """Toglie le parole iniziali uguali: «Acer E», «Acer H» → «E», «H»."""
    parole = [n.split() for n in nomi]
    comuni = 0
    while (parole and all(len(p) > comuni + 1 for p in parole)
           and len({p[comuni] for p in parole}) == 1):
        comuni += 1
    return [" ".join(p[comuni:]) for p in parole]


def descrivi_valori(nomi, valori, filtro, entra=None):
    """«Acer E 40% · Acer H 60% · oscuramento 10%»; se `entra(testo)` dice di no,
    prova versioni più corte (nomi brevi, poi «osc.»)."""
    testo, tutti = "", t("Tutti")
    for nomi_usati, scuro in ((nomi, t("oscuramento")), (nomi_brevi(nomi), t("oscuramento")),
                              (nomi_brevi(nomi), t("osc."))):
        if len(set(valori)) <= 1:
            testo = f"{tutti} {valori[0]}%" if valori else ""
        else:
            testo = " · ".join(f"{nome} {v}%" for nome, v in zip(nomi_usati, valori))
        testo += f" · {scuro} {filtro}%" if filtro else ""
        if entra is None or entra(testo):
            break
    return testo


def suggerimento_tray(nomi, valori, filtro):
    """Il testo al passaggio sull'icona: Windows ne accetta al massimo 127 caratteri."""
    testo = " · ".join(f"{m} {v}%" for m, v in zip(nomi, valori))
    scuro = t("oscuramento")
    return (testo + (f" · {scuro} {filtro}%" if filtro else ""))[:127]


def pulisci_nome(nome):
    """Spazi normalizzati e lunghezza massima; stringa vuota se non resta niente."""
    return " ".join(nome.split())[:LUNGHEZZA_NOME]
