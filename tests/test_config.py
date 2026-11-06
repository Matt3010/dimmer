import json

from dimmer.config import PRESET_DEFAULT, Config


def test_prima_volta_preset_di_fabbrica(tmp_path):
    cfg = Config(str(tmp_path / "Dimmer" / "config.json"))
    cfg.assicura_preset()
    assert cfg.preset == PRESET_DEFAULT and cfg.filtro == 0 and cfg.lingua == "auto"


def test_preset_di_fabbrica_nella_lingua_scelta(tmp_path):
    cfg = Config(str(tmp_path / "config.json"))
    cfg.assicura_preset({"Lavoro": "Work", "Film": "Movie", "Notte": "Night"}.get)
    assert list(cfg.preset) == ["Work", "Movie", "Night"]


def test_preset_eliminati_non_tornano(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"filtro": 5, "preset": {"Mio": {"monitor": 30, "filtro": 0}}}))
    cfg = Config(str(p))
    cfg.assicura_preset()
    assert list(cfg.preset) == ["Mio"] and cfg.filtro == 5


def test_file_rotto_riparte_pulito_e_salva(tmp_path):
    p = tmp_path / "config.json"
    p.write_text("{rotto")
    cfg = Config(str(p))
    cfg.filtro = 7
    cfg.salva()
    assert json.loads(p.read_text())["filtro"] == 7
    assert not (tmp_path / "config.json.tmp").exists()
