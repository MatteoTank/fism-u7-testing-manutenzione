import pytest
from unittest.mock import patch, MagicMock
import spedizioni
import requests
from spedizioni import ServizioSpedizioniNonDisponibile

@pytest.fixture(autouse=True)
def stato_pulito():
    """Sovrascrive la fixture autouse del conftest: questi test non toccano il server."""
    yield

def risposta_finta(status: int, corpo: dict):
    
    return risposta_finta

@patch("spedizioni.requests.get")
def test_costo_letto_dalla_risposta(mock_get):
    # Arrange: costruisco una risposta HTTP finta
    risposta_finta = MagicMock()
    risposta_finta.status_code = 200
    risposta_finta.json.return_value = {"costo": 4.9}
    mock_get.return_value = risposta_finta

    # Act: chiamo la funzione che voglio testare
    costo = spedizioni.costo_spedizione("50100", 1.5)

    # Assert: verifico che il costo sia quello atteso
    assert costo == 4.9

    args, kwargs = mock_get.call_args

    # Verifica che l'URL (primo argomento posizionale) sia corretto
    assert args[0] == "http://localhost:8001/tariffa"

    # Verifica che i parametri passati nella query string siano corretti
    assert kwargs["params"] == {"cap": "50100", "peso": 1.5}

@patch("spedizioni.requests.get")
def test_chiamata_ha_un_timeout(mock_get):
    risposta_finta = MagicMock()
    risposta_finta.json.return_value = {"costo": 4.9}
    mock_get.return_value = risposta_finta

    costo = spedizioni.costo_spedizione("50100", 1.5)

    _, kwargs = mock_get.call_args

    assert "timeout" in kwargs
    assert kwargs["timeout"] <= 3

@pytest.mark.parametrize("guasto", [
    requests.Timeout("il corriere non risponde"),
    requests.ConnectionError("il corriere è spento"),
])

@patch("spedizioni.requests.get")
def test_errore_dominio(mock_get, guasto):
    mock_get.side_effect = guasto

    with pytest.raises(ServizioSpedizioniNonDisponibile):
        spedizioni.costo_spedizione("50100", 1.5)

@patch("spedizioni.requests.get")
def test_corriere_risponde_503(mock_get):
    risposta_finta = MagicMock()
    risposta_finta.status = 503
    risposta_finta.raise_for_status.side_effect = requests.HTTPError("503")
    mock_get.return_value = risposta_finta

    with pytest.raises(ServizioSpedizioniNonDisponibile):
        spedizioni.costo_spedizione("50100", 1.5)