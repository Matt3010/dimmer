"""Dimmer: luminosità dei monitor dalla tray di Windows (DDC/CI).

Clic sinistro sull'icona: pannello con le schede Monitor e Preset.
Rotellina sull'icona: luminosità su/giù (sotto lo 0% entra l'oscuramento).
Clic destro: preset, avvio con Windows, esci.
"""
from dimmer.app import main

if __name__ == "__main__":
    main(__file__)
