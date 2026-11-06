"""Disegno con Pillow: forme antialias, sfumature, icone e la manopola degli slider.
Quello che si ridisegna spesso è in cache."""
import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

from .tema import BASE, FONT_ICONE, HAIRLINE, MANOPOLA, SS


def hex_rgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mescola(c1, c2, t):
    """Come color-mix(in srgb, c2 t%, c1)."""
    a, b = hex_rgb(c1), hex_rgb(c2)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def rettangolo(w, h, raggio, fondo, bordo=None, sfondo=None):
    """Rettangolo arrotondato antialias, con bordo da 1px se richiesto."""
    img = Image.new("RGB", (w * SS, h * SS), sfondo or BASE)
    ImageDraw.Draw(img).rounded_rectangle(
        (0, 0, w * SS - 1, h * SS - 1), raggio * SS, fill=fondo,
        outline=bordo, width=SS if bordo else 0)
    return img.resize((w, h), Image.LANCZOS)


def isola(w, h, raggio, fondo, bordo, trasparente):
    """Lo sfondo di una finestra con gli angoli trasparenti. Windows rende trasparente solo
    il colore esatto `trasparente`: i pixel sfumati verso di lui resterebbero come alone scuro.
    Quindi il bordo si sfuma verso il fondo del pannello e il contorno esterno è netto."""
    img = rettangolo(w, h, raggio, fondo, bordo, sfondo=fondo)
    forma = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(forma).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), raggio * SS, fill=255)
    dentro = forma.resize((w, h), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)
    risultato = Image.new("RGB", (w, h), trasparente)
    risultato.paste(img, (0, 0), dentro)
    return risultato


def gradiente(w, h, sinistra, destra):
    a, b = hex_rgb(sinistra), hex_rgb(destra)
    riga = Image.new("RGB", (w, 1))
    riga.putdata([tuple(round(x + (y - x) * i / max(1, w - 1)) for x, y in zip(a, b)) for i in range(w)])
    return riga.resize((w, h))


def gradiente_v(w, h, alto, basso):
    return gradiente(h, w, alto, basso).transpose(Image.Transpose.ROTATE_270).transpose(
        Image.Transpose.FLIP_LEFT_RIGHT)


def barra_piena(w, h, frazione, colori, fondo):
    """Binario arrotondato con la parte piena sfumata (l'indicatore della rotellina)."""
    img = rettangolo(w, h, h // 2, fondo)
    if frazione > 0:
        lp = max(h, int(w * frazione))
        maschera = rettangolo(lp, h, h // 2, "#ffffff", sfondo="#000000").convert("L")
        img.paste(gradiente(lp, h, *colori), (0, 0), maschera)
    return img


# ---------- icone ----------
@lru_cache(maxsize=None)
def _font_icone(px):
    return ImageFont.truetype(FONT_ICONE, px)


_foto_icone = {}


def icona_foto(glifo, px, colore):
    """Il glifo come immagine trasparente, centrata sul disegno vero
    (non sulla riga del testo, che lo sposta in alto e di lato)."""
    chiave = (glifo, px, colore)
    if chiave not in _foto_icone:
        lato = (px + 4) * SS
        img = Image.new("RGBA", (lato, lato), hex_rgb(colore) + (0,))
        font = _font_icone(px * SS)
        x0, y0, x1, y1 = font.getbbox(glifo)
        ImageDraw.Draw(img).text(((lato - (x1 - x0)) / 2 - x0, (lato - (y1 - y0)) / 2 - y0),
                                 glifo, font=font, fill=colore)
        _foto_icone[chiave] = ImageTk.PhotoImage(img.resize((px + 4, px + 4), Image.LANCZOS))
    return _foto_icone[chiave]


@lru_cache(maxsize=None)
def icona_larghezza(glifo, px):
    """Larghezza del disegno vero del glifo, in pixel."""
    x0, _, x1, _ = _font_icone(px * SS).getbbox(glifo)
    return (x1 - x0) / SS


# ---------- manopola degli slider ----------
R_MANOPOLA = 10


@lru_cache(maxsize=None)
def manopola(colore, stato):
    """La manopola alla Windows 11 già disegnata (a scala SS, con ombra morbida):
    cerchio fisso e pallino che cresce col mouse sopra («hover») e si stringe se premi.
    Si disegna una volta sola per colore e stato, non a ogni movimento."""
    R, s = R_MANOPOLA, SS
    lato = (2 * R + 8) * s
    c = lato / 2
    ombra = Image.new("L", (lato, lato), 0)
    ImageDraw.Draw(ombra).ellipse((c - R * s, c - R * s + s, c + R * s, c + R * s + s), fill=120)
    ombra = ombra.filter(ImageFilter.GaussianBlur(1.2 * s))
    img = Image.new("RGBA", (lato, lato), (0, 0, 0, 0))
    img.putalpha(ombra)
    d = ImageDraw.Draw(img)
    d.ellipse((c - R * s, c - R * s, c + R * s, c + R * s), fill=MANOPOLA, outline=HAIRLINE, width=s)
    r = {"premuto": 4, "hover": 6.5}.get(stato, 5)
    d.ellipse((c - r * s, c - r * s, c + r * s, c + r * s), fill=colore)
    return img


# ---------- icona della tray ----------
@lru_cache(maxsize=64)
def icona_tray(livello, scuro):
    """Un sole più o meno acceso, o una luna quando c'è l'oscuramento."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if scuro:
        d.ellipse((10, 10, 54, 54), fill=(143, 168, 255, 255))
        d.ellipse((24, 2, 66, 44), fill=(0, 0, 0, 0))    # falce di luna
        return img
    v = int(80 + 175 * livello / 100)
    colore = (v, v, int(v * 0.6), 255)
    d.ellipse((18, 18, 46, 46), fill=colore)
    for i in range(8):
        a = i * math.pi / 4
        d.line((32 + 20 * math.cos(a), 32 + 20 * math.sin(a),
                32 + 29 * math.cos(a), 32 + 29 * math.sin(a)), fill=colore, width=4)
    return img
