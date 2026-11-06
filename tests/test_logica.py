from dimmer.logica import (MAX_FILTRO, descrivi_valori, media, nomi_brevi, passo_rotella,
                           pulisci_nome, suggerimento_tray, valori_preset)


def test_rotella_giu_abbassa_i_monitor_poi_scurisce():
    assert passo_rotella([10, 20], 0, -5) == ([5, 15], 0)
    assert passo_rotella([0, 0], 0, -5) == ([0, 0], 5)
    assert passo_rotella([0, 0], MAX_FILTRO, -5) == ([0, 0], MAX_FILTRO)


def test_rotella_su_toglie_prima_il_filtro():
    assert passo_rotella([0, 0], 10, 5) == ([0, 0], 5)
    assert passo_rotella([95, 50], 0, 10) == ([100, 60], 0)


def test_media_intera_e_senza_monitor():
    assert media([40, 61]) == 50
    assert media([]) == 0


def test_valori_preset_numero_lista_e_monitor_in_piu():
    assert valori_preset({"monitor": 70, "filtro": 0}, 2) == ([70, 70], 0)
    assert valori_preset({"monitor": [30, 50]}, 2) == ([30, 50], 0)
    assert valori_preset({"monitor": [30, 50], "filtro": 10}, 3) == ([30, 50, 50], 10)
    assert valori_preset({"monitor": [30, 50]}, 1) == ([30], 0)


def test_nomi_brevi():
    assert nomi_brevi(["Acer E", "Acer H"]) == ["E", "H"]
    assert nomi_brevi(["Dell", "LG"]) == ["Dell", "LG"]
    assert nomi_brevi(["Acer", "Acer"]) == ["Acer", "Acer"]
    assert nomi_brevi([]) == []


def test_descrizione_completa_e_accorciata():
    nomi = ["Acer E", "Acer H"]
    assert descrivi_valori(nomi, [75, 75], 0) == "Tutti 75%"
    assert descrivi_valori(nomi, [0, 0], 10) == "Tutti 0% · oscuramento 10%"
    assert descrivi_valori(nomi, [39, 87], 0) == "Acer E 39% · Acer H 87%"
    corta = descrivi_valori(nomi, [100, 85], 85, entra=lambda t: len(t) <= 26)
    assert corta == "E 100% · H 85% · osc. 85%"


def test_suggerimento_tray_al_massimo_127_caratteri():
    assert suggerimento_tray(["A", "B"], [1, 2], 3) == "A 1% · B 2% · oscuramento 3%"
    assert len(suggerimento_tray(["x" * 100] * 3, [1, 2, 3], 0)) == 127


def test_pulisci_nome():
    assert pulisci_nome("  Serata   film  ") == "Serata film"
    assert pulisci_nome("   ") == ""
    assert len(pulisci_nome("a" * 40)) == 24
