"""Tutto quello che passa per le API di Windows (ctypes e registro), in un posto solo."""
import ctypes
import os
import sys
import threading
import winreg
from ctypes import wintypes as wt

user32 = ctypes.WinDLL("user32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32")
gdi32 = ctypes.WinDLL("gdi32")
dwmapi = ctypes.WinDLL("dwmapi")

LRESULT = ctypes.c_ssize_t
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wt.WPARAM, wt.LPARAM)
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wt.HINSTANCE, wt.DWORD]
user32.SetWindowsHookExW.restype = wt.HHOOK
user32.CallNextHookEx.argtypes = [wt.HHOOK, ctypes.c_int, wt.WPARAM, wt.LPARAM]
user32.CallNextHookEx.restype = LRESULT
user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, wt.UINT]
user32.SetLayeredWindowAttributes.argtypes = [wt.HWND, wt.DWORD, ctypes.c_ubyte, wt.DWORD]

SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_NOACTIVATE = 0x1, 0x2, 0x4, 0x10
HWND_TOPMOST = -1


def dpi_reale():
    """Coordinate in pixel veri: servono uguali per finestre, icona della tray e mouse."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass


def carica_font_privati(percorsi):
    """Font visibili solo a questo programma, senza installarli. Vero se ci sono tutti."""
    if not all(os.path.exists(p) for p in percorsi):
        return False
    for p in percorsi:
        gdi32.AddFontResourceExW(p, 0x10, 0)   # FR_PRIVATE
    return True


def colorref(hex_colore):
    r, g, b = (int(hex_colore[i:i + 2], 16) for i in (1, 3, 5))
    return r | g << 8 | b << 16


# ---------- finestre ----------
def hwnd(win):
    return int(win.wm_frame(), 16)


def stile_esteso(win, click_through=False):
    """Senza tasto nella barra e senza rubare il focus; con `click_through` il mouse ci passa attraverso."""
    win.update_idletasks()
    h = hwnd(win)
    ex = user32.GetWindowLongW(h, -20) | 0x80 | 0x08000000      # TOOLWINDOW | NOACTIVATE
    if click_through:
        ex |= 0x80000 | 0x20                                     # LAYERED | TRANSPARENT
    user32.SetWindowLongW(h, -20, ex)


def area_lavoro():
    """Lo schermo principale senza la barra delle applicazioni."""
    r = wt.RECT()
    user32.SystemParametersInfoW(48, 0, ctypes.byref(r), 0)       # SPI_GETWORKAREA
    return r.left, r.top, r.right, r.bottom


def schermo_virtuale():
    """Il rettangolo che contiene tutti i monitor: x, y, larghezza, altezza."""
    gm = user32.GetSystemMetrics
    return gm(76), gm(77), gm(78), gm(79)


def metti_in_cima(h, sotto_a=None):
    """In cima a tutto (sopra la barra) o subito sotto `sotto_a`, senza attivare né ridisegnare."""
    user32.SetWindowPos(h, sotto_a or HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)


def sposta_e_dissolvi(h, x, y, alpha, chiave):
    """Posizione e opacità nello stesso fotogramma (chiave = colore degli angoli trasparenti)."""
    user32.SetWindowPos(h, None, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
    user32.SetLayeredWindowAttributes(h, chiave, round(alpha * 255), 0x1 | 0x2)  # COLORKEY | ALPHA


def aspetta_fotogramma():
    dwmapi.DwmFlush()


# ---------- icona nella tray e rotellina ----------
class NOTIFYICONIDENTIFIER(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("hWnd", wt.HWND), ("uID", wt.UINT),
                ("guidItem", ctypes.c_byte * 16)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wt.POINT), ("mouseData", wt.DWORD), ("flags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


def rettangolo_icona_tray(icona_pystray):
    """Dove sta l'icona nella tray; None se non c'è (o se è nascosta nella freccetta)."""
    h = getattr(icona_pystray, "_hwnd", None)
    if not h:
        return None
    # pystray registra l'icona passando "hID" invece di "uID": per Windows l'ID resta 0
    nid = NOTIFYICONIDENTIFIER(ctypes.sizeof(NOTIFYICONIDENTIFIER), h, 0)
    r = wt.RECT()
    if shell32.Shell_NotifyIconGetRect(ctypes.byref(nid), ctypes.byref(r)) != 0:
        return None
    return r.left, r.top, r.right, r.bottom


class HookRotella:
    """Hook globale del mouse: la rotellina sopra `area` chiama `al_giro(+1/-1)`
    (dal thread dell'hook) e non arriva ad altre finestre."""

    def __init__(self, al_giro):
        self.area = None
        self._al_giro = al_giro
        self._proc = HOOKPROC(self._hook)            # va tenuto in vita finché c'è l'hook
        threading.Thread(target=self._esegui, daemon=True).start()

    def _hook(self, n_code, w_param, l_param):
        area = self.area
        if n_code == 0 and w_param == 0x020A and area:   # WM_MOUSEWHEEL
            ms = ctypes.cast(l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            sx, su, dx, giu = area
            if sx <= ms.pt.x < dx and su <= ms.pt.y < giu:
                self._al_giro(1 if ctypes.c_short(ms.mouseData >> 16).value > 0 else -1)
                return 1
        return user32.CallNextHookEx(None, n_code, w_param, l_param)

    def _esegui(self):
        user32.SetWindowsHookExW(14, self._proc, None, 0)   # WH_MOUSE_LL
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))


# ---------- avvio con Windows ----------
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def comando_avvio(script):
    """Cosa lancia Windows all'accesso: l'exe stesso, o pythonw con lo script."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return f'"{pythonw}" "{os.path.abspath(script)}"'


_mutex = None


def unica_istanza(nome):
    """Vero se nessun'altra copia è già aperta (un mutex col nome dell'app)."""
    global _mutex
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.restype = wt.HANDLE
    _mutex = kernel32.CreateMutexW(None, False, f"Local\\{nome}")
    return ctypes.get_last_error() != 183          # ERROR_ALREADY_EXISTS


def avvio_attivo(nome):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, nome)
            return True
    except OSError:
        return False


def imposta_avvio(nome, comando):
    """`comando` None toglie l'avvio con Windows."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if comando:
            winreg.SetValueEx(k, nome, 0, winreg.REG_SZ, comando)
        elif avvio_attivo(nome):
            winreg.DeleteValue(k, nome)
