# Dimmer

Luminosità dei monitor dalla tray di Windows, via DDC/CI. Per uso personale.

- **Clic sinistro**: pannello con le schede *Monitor* (slider per tutti e per ciascun monitor, più «Oscuramento» sotto lo 0%) e *Preset*.
- **Rotellina sull'icona**: luminosità su/giù; sotto lo 0% entra l'oscuramento.
- **Clic destro**: preset, lingua (automatica, italiano, inglese), avvio con Windows, esci.

## Avvio

```
pip install -r requirements.txt
pythonw dimmer.pyw
```

I monitor devono avere DDC/CI attivo (di solito nel menu del monitor).
Preset e oscuramento stanno in `%APPDATA%\Dimmer\config.json`.

## Com'è fatto

| modulo | cosa fa |
|---|---|
| `logica.py` | regole pure (rotellina, preset, descrizioni): niente Tk né Windows |
| `config.py` | carica e salva la configurazione (scrittura atomica) |
| `lingua.py` | italiano e inglese: testo italiano come chiave, dizionario inglese (un test controlla che non manchi niente) |
| `monitor.py` | DDC/CI in un thread; più valori ravvicinati → solo l'ultimo |
| `win32.py` | tutte le API di Windows: finestre, hook della rotellina, icona della tray, avvio |
| `tema.py` | colori, misure, font e icone (il tema scuro di SendLater) |
| `grafica.py` | disegno con Pillow, con cache per quello che si ridisegna spesso |
| `animazione.py` | entrate e uscite alla Windows 11, sincronizzate col refresh |
| `widget.py` | slider, schede, righe dei preset, tasti, campo di testo |
| `finestre.py` | superficie a isola, velo dell'oscuramento, indicatore della rotellina |
| `pannello.py` | il pannello con le due schede |
| `app.py` | stato, icona nella tray, comandi tra i thread |

Test: `python -m pytest`

## Font

`font/` contiene Inter (licenza OFL, `font/OFL-Inter.txt`) ricavato dal font variabile
con `strumenti/crea_font.py`; lo carica solo Dimmer, senza installarlo.
Se manca, si usa Segoe UI Variable.

## Licenza

Codice sotto licenza [MIT](LICENSE). Il font Inter in `font/` ha la sua licenza (SIL OFL 1.1).
