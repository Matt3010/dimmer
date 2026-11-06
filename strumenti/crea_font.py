"""Ricava Inter statico (TTF) dal woff2 variabile usato da SendLater.

GDI/Tk non sanno scegliere i pesi di un font variabile: si generano tre famiglie
separate («Inter SL», «Inter SL Medium», «Inter SL Semibold»), ognuna di peso normale.
Uso: python strumenti/crea_font.py <cartella files di @fontsource-variable/inter>
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SORGENTE = sys.argv[1]
DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "font")
PESI = {"Inter SL": 400, "Inter SL Medium": 500, "Inter SL Semibold": 590}

os.makedirs(DEST, exist_ok=True)
for famiglia, peso in PESI.items():
    font = TTFont(os.path.join(SORGENTE, "inter-latin-wght-normal.woff2"))
    font.flavor = None
    font = instancer.instantiateVariableFont(font, {"wght": peso, "opsz": 14} if "opsz" in [
        a.axisTag for a in font["fvar"].axes] else {"wght": peso})
    nomi = font["name"]
    for rec in list(nomi.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            nomi.removeNames(nameID=rec.nameID)
    nomi.setName(famiglia, 1, 3, 1, 0x409)
    nomi.setName("Regular", 2, 3, 1, 0x409)
    nomi.setName(famiglia, 4, 3, 1, 0x409)
    nomi.setName(famiglia.replace(" ", ""), 6, 3, 1, 0x409)
    font["OS/2"].usWeightClass = 400
    font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0b1100001) | 0b1000000  # REGULAR
    font["head"].macStyle = 0
    file = os.path.join(DEST, famiglia.replace(" ", "") + ".ttf")
    font.save(file)
    print(file)
