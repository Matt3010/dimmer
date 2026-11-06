"""Crea dist/Dimmer.exe (un file solo, senza bisogno di Python).
Uso: pip install pyinstaller && python strumenti/crea_exe.py"""
import os
import subprocess
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADICE)

from dimmer import __version__  # noqa: E402
from dimmer.grafica import icona_tray  # noqa: E402


def crea_icona(percorso):
    """L'icona dell'exe: il sole della tray, in tutte le misure che usa Windows."""
    icona_tray(100, False).save(percorso, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])


def crea_info_versione(percorso):
    """Nome, versione e autore che Windows mostra nelle proprietà del file."""
    v = tuple(int(x) for x in __version__.split(".")) + (0,)
    with open(percorso, "w", encoding="utf8") as f:
        f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={v}, prodvers={v}),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'Matteo Scanferla'),
    StringStruct('FileDescription', 'Dimmer - monitor brightness from the tray'),
    StringStruct('FileVersion', '{__version__}'),
    StringStruct('InternalName', 'Dimmer'),
    StringStruct('LegalCopyright', 'MIT License'),
    StringStruct('OriginalFilename', 'Dimmer.exe'),
    StringStruct('ProductName', 'Dimmer'),
    StringStruct('ProductVersion', '{__version__}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])])
""")


def main():
    build = os.path.join(RADICE, "build")
    os.makedirs(build, exist_ok=True)
    icona, info = os.path.join(build, "dimmer.ico"), os.path.join(build, "versione.txt")
    crea_icona(icona)
    crea_info_versione(info)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
        "--name", "Dimmer", "--icon", icona, "--version-file", info,
        "--add-data", f"{os.path.join(RADICE, 'font')}{os.pathsep}font",
        # non servono e pesano: NumPy (lo tira dentro Pillow, ~27 MB) e la crittografia (~5 MB)
        "--exclude-module", "numpy", "--exclude-module", "ssl", "--exclude-module", "_ssl",
        "--exclude-module", "_hashlib",
        "--distpath", os.path.join(RADICE, "dist"), "--workpath", build, "--specpath", build,
        os.path.join(RADICE, "dimmer.pyw"),
    ], check=True, cwd=RADICE)
    print("creato", os.path.join(RADICE, "dist", "Dimmer.exe"))


if __name__ == "__main__":
    main()
