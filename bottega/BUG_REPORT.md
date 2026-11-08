# BUGS REPORT

## BUG-001: Sad path carrello

- **Endpoint:** POST /api/carrello
- **Passi per riprodurlo:** Parametrizzare i vari body con

    ```python
        pytest.mark.parametrize("body,atteso", [
            ({"prodotto_id": 2, "quantita": -3}, 400),
            ({"prodotto_id": 2, "quantita": 0}, 400),
            ({"prodotto_id": 2, "quantita": "2"}, 400),
            ({"prodotto_id": 2}, 400),
            ({"prodotto_id": 999, "quantita": 1}, 404),
            ({"prodotto_id": 3, "quantita": 99}, 409)
        ])
        def test_sad_path_carrello(body, atteso, base_url, auth):
        risposta = requests.post(
            f"{base_url}/api/carrello",
            json=body,
            headers=auth,
            timeout=5
        )

    assert risposta.status_code == atteso
    ```

- **Elenco errori**
    1. **Atteso (contratto):** 400 con {"errore": "Quantità negativa"}
    2. **Atteso (contratto):** 400 con {"errore": "Quantità zero"}
    3. **Atteso (contratto):** 400 con {"errore": "Tipo sbagliato"}
    4. **Atteso (contratto):** 400 con {"errore": "Campo mancante"}
- **Ottenuto:**
    1. Status code: 201
    2. Status code: 201
    3. Status code: 500
    4. Status code: 500
- **Gravità:** Alta: perchè i codici di response sono completamente sbagliate
- **Test che lo dimostra:** tests/test_sad_path_carrello.py

## BUG-002: Messaggio di errore

- **Endpoint:** POST /api/login
- **Passi per riprodurlo:** Parametrizzare i vari body con

    ```python
        @pytest.mark.parametrize("body",[
            {"username":"Gennaro", "password":"password123"},
            {"username":"Mario", "password":"password"}
        ])
        def test_sicurezza(body, base_url):
        risposta = requests.post(
            f"{base_url}/api/login",
            json=body,
            timeout=5
        )

        assert risposta.status_code == 401
        assert risposta.json()['errore'] == "credenziali non valide"
    ```

- **Elenco errori**
    1. **Atteso (contratto):** 401 con {"errore": "Credenziali non valide"}
    2. **Atteso (contratto):** 401 con {"errore": "Credenziali non valide"}
- **Ottenuto:**
    1. {"errore": "utente inesistente"}
    2. {"errore": "utente inesistente"}
- **Gravità:** Alta: perchè i messaggi devono essere ambigui per non dare aiuti ad un attacker
- **Test che lo dimostra:** tests/test_sicurezza.py

## BUG-003: Codice errore bloccante

- **Endpoint:** POST /api/login
- **Passi per riprodurlo:** Parametrizzare i vari body con

    ```python
        @pytest.mark.parametrize("body, code", [
            ('{"username": "mario"', 400),
            ("non sono json",400),
            ("",400),
            ('{"username": "mario"}',400),
            ('{"password": "password123"}',400),
            ("[]",400)
        ])
        def test_request_body_failure(body, code):
            response = requests.post(f"{BASE_URL}/api/login", data=body, headers={"Content-Type": "application/json"}, timeout=5)
            assert response.status_code == code
            assert "errore" in response.json()
    ```

- **Elenco errori**
    1. **Atteso (contratto):** 400
- **Ottenuto:** 500 con output HTML
- **Gravità:** Bloccante: perchè il server si rompe perchè non è stato gestito l'errore
- **Test che lo dimostra:** tests/test_health_soluzione.py
