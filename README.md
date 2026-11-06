# Dimmer

**Control your monitors' real brightness from the Windows tray.** Dimmer talks to your monitors over DDC/CI, so it changes the actual backlight instead of putting a filter on top, and it looks and feels like a native Windows 11 flyout.

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
- Python 3.11 or newer

> Laptop screens are not supported: Dimmer controls external monitors.

## Install

1. **Install Python** (skip if you already have it). Open *Terminal* and run:
   ```
   winget install Python.Python.3.12
   ```
   or download it from [python.org](https://www.python.org/downloads/windows/).

2. **Download Dimmer**: click **Code → Download ZIP** at the top of this page and extract it to a folder you'll keep, for example `Documents\Dimmer`.

3. **Install what it needs**: open *Terminal* in that folder (right click on the folder → *Open in Terminal*) and run:
   ```
   pip install -r requirements.txt
   ```

4. **Start it**: double click `dimmer.pyw`. A sun icon appears in the tray, next to the clock.

5. *(Optional)* **Start with Windows**: right click the icon → **Start with Windows**.

Tip: if the icon is hidden behind the **^** arrow, drag it onto the taskbar so it's always visible and the mouse wheel works on it.

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
- **Double clicking `dimmer.pyw` does nothing**: run `pythonw dimmer.pyw` from *Terminal* in the Dimmer folder.

## Uninstall

1. Right click the icon → turn off **Start with Windows** → **Quit**.
2. Delete the Dimmer folder.
3. *(Optional)* delete your saved presets: `%APPDATA%\Dimmer`.

## License

[MIT](LICENSE). Includes the [Inter](https://rsms.me/inter/) font (SIL Open Font License 1.1).
