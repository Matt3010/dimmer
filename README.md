# Dimmer

**Control your monitors' real brightness from the Windows tray.** Dimmer talks to your monitors over DDC/CI, so it changes the actual backlight instead of putting a filter on top, and it looks and feels like a native Windows 11 flyout.

[![Download](https://img.shields.io/github/v/release/Matt3010/dimmer?label=download&color=2f9e5e)](https://github.com/Matt3010/dimmer/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Windows 10/11](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows&logoColor=white)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)

<p>
  <img src="docs/displays.png" alt="Dimmer panel: brightness sliders for each monitor" width="320">
  <img src="docs/presets.png" alt="Dimmer panel: brightness presets" width="320">
</p>

## Features

- **Real monitor brightness** for every external monitor, one by one or all together.
- **Even darker than 0%**: a dimming layer for late nights, when the monitor's minimum is still too bright.
- **Presets** like *Work*, *Movie* and *Night*: one click from the panel or the tray menu.
- **Mouse wheel on the tray icon** to change brightness without opening anything.
- **Start with Windows**, Italian and English, dark Windows 11 look.

<p>
  <img src="docs/new-preset.png" alt="Creating a new preset" width="320">
  <img src="docs/wheel.png" alt="Brightness indicator shown when scrolling on the tray icon" width="244">
</p>

## Requirements

- Windows 10 or 11
- External monitors with **DDC/CI** turned on. Most monitors have it; look for *DDC/CI* in the monitor's own menu (the buttons on the monitor) and make sure it's enabled.

> Laptop screens are not supported: Dimmer controls external monitors.

## Install

1. **Download [Dimmer.exe](https://github.com/Matt3010/dimmer/releases/latest/download/Dimmer.exe)** from the [latest release](https://github.com/Matt3010/dimmer/releases/latest). Nothing else is needed.
2. Put it in a folder you'll keep, for example `Documents\Dimmer`, and **double click it**. A sun icon appears in the tray, next to the clock.
3. *(Optional)* **Start with Windows**: right click the icon → **Start with Windows**.

> **"Windows protected your PC"?** Dimmer isn't code-signed (signing costs money), so SmartScreen warns about it the first time. Click **More info → Run anyway**.

Tip: if the icon is hidden behind the **^** arrow, drag it onto the taskbar so it's always visible and the mouse wheel works on it.

<details>
<summary>Run from source instead (Python 3.11+)</summary>

```
git clone https://github.com/Matt3010/dimmer.git
cd dimmer
pip install -r requirements.txt
pythonw dimmer.pyw
```

To build the exe yourself: `pip install pyinstaller` and `python strumenti/crea_exe.py` (it ends up in `dist\`).
</details>

## How to use it

| Action | What happens |
|---|---|
| **Left click** on the icon | Opens the panel: *Displays* tab with the sliders, *Presets* tab with your presets |
| **Mouse wheel** on the icon | Brightness up/down; scrolling down past 0% dims further |
| **Right click** on the icon | Presets, language, start with Windows, quit |

**Presets**: in the *Presets* tab, **New preset** saves the current brightness under a name. Hover a preset to update it with the current values (💾) or delete it (🗑, click twice to confirm).

## Troubleshooting

- **A monitor doesn't appear or doesn't change**: DDC/CI is probably off. Enable it in the monitor's menu, then quit Dimmer (right click → Quit) and start it again.
- **The mouse wheel does nothing on the icon**: the icon is hidden behind the **^** arrow. Drag it onto the taskbar.
- **Something else goes wrong**: Dimmer writes what it finds and any error to `%APPDATA%\Dimmer\dimmer.log`. Attach it when you [open an issue](https://github.com/Matt3010/dimmer/issues).

## Uninstall

1. Right click the icon → turn off **Start with Windows** → **Quit**.
2. Delete `Dimmer.exe` (or the Dimmer folder).
3. *(Optional)* delete your saved presets and the log: `%APPDATA%\Dimmer`.

## License

[MIT](LICENSE). Includes the [Inter](https://rsms.me/inter/) font (SIL Open Font License 1.1).
