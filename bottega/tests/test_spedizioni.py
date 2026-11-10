import pytest
from unittest.mock import patch, MagicMock
import spedizioni

@pytest.fixture(autouse=True)
def stato_pulito():
    yield

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

    mock_get.assert_called_once_with("http://localhost:8001/tariffa", params={"cap": "50100", "peso": 1.5}) 

    """ args, kwargs = mock_get.call_args

    # Verifica che l'URL (primo argomento posizionale) sia corretto
    assert args[0] == "http://localhost:8001/tariffa"

    # Verifica che i parametri passati nella query string siano corretti
    assert kwargs["params"] == {"cap": "50100", "peso": 1.5} """