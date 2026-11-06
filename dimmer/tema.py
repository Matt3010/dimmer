"""Colori, misure, font e icone: il tema scuro di SendLater (frontend/src/styles/tokens.css)."""
import os

# colori
BASE = "#14171c"                       # --base
HAIRLINE = "#2c2e33"                   # --hairline: bianco al 10% sulla base
SUNKEN, SUNKEN_HOVER = "#202328", "#2c2e33"
MANOPOLA = "#3a3d44"                   # il cerchio esterno della manopola degli slider
INK, INK_2, INK_3 = "#eef1f5", "#9aa4b2", "#6f7987"
ON_ACCENT = "#0e1116"
ACCENTO = ("#c9d0d9", "#ffffff")       # --accent-grad, in orizzontale
ME_CHIARO = "#6f9bff"                  # --me, il blu di SendLater, schiarito per il buio
NOTTE = ("#2559cc", "#5b8dff")
PERICOLO, BENE = "#ff6b5e", "#3fbf75"  # --danger e --ok al buio
TRASPARENTE = "#010203"                # colore chiave degli angoli fuori dall'isola

# misure
R_LG = 20                              # --r-lg
CARD_PAD = 12                          # --card-pad
R_IN = R_LG - CARD_PAD - 1             # --r-in: campi e tasti dentro la scheda (7)
ENTRA = 6                              # quanto le righe dei preset entrano nel padding
R_FLAT = R_LG - (CARD_PAD - ENTRA)     # angoli concentrici con quelli del pannello
SS = 3                                 # si disegna 3 volte più grande e si riduce: bordi lisci

# font: Inter ricavato da SendLater (strumenti/crea_font.py), caricato solo per Dimmer
CARTELLA_FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "font")
FILE_FONT = [os.path.join(CARTELLA_FONT, f) for f in ("InterSL.ttf", "InterSLMedium.ttf", "InterSLSemibold.ttf")]
HA_INTER = all(os.path.exists(f) for f in FILE_FONT)
FAM, FAM_M, FAM_S = (("Inter SL", "Inter SL Medium", "Inter SL Semibold") if HA_INTER else
                     ("Segoe UI Variable Text", "Segoe UI Variable Text Semibold",
                      "Segoe UI Variable Text Semibold"))
F_TITOLO = (FAM_S, -15)
F_TITOLO_P = (FAM_S, -14)
F_LABEL = (FAM_M, -13)
F_VALORE = (FAM_M, -12)
F_CHIP = (FAM_M, -12)
F_HINT = (FAM, -12)
F_CAMPO = (FAM, -14)
F_TASTO_PRIMARIO = (FAM_S, -12)

# icone (Segoe Fluent Icons, il font di sistema di Windows 11)
FONT_ICONE = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "SegoeIcons.ttf")
ICONA_SOLE, ICONA_LUNA, ICONA_OK = "\ue706", "\ue708", "\ue73e"
ICONA_SALVA, ICONA_CESTINO = "\ue74e", "\ue74d"
ICONA_PIU, ICONA_STELLA = "\ue710", "\ue734"
ICONE_PRESET = {"Lavoro": "\ue821", "Film": "\ue714", "Notte": ICONA_LUNA,
                "Work": "\ue821", "Movie": "\ue714", "Night": ICONA_LUNA}
