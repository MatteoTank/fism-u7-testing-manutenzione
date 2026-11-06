import pytest
import requests

@pytest.fixture
def base_url():
    return "http://localhost:8000"

@pytest.fixture
def token(base_url):
    login = requests.post(f"{base_url}/api/login", json={"username":"mario", "password":"password123"}, timeout=5)
    return login.json()["token"]

@pytest.fixture
def auth(token):
    return {"Authorization": f"Bearer {token}"}

# chiamata POST per resettare il carrello
@pytest.fixture(autouse=True)
def stato_pulito(base_url):
    requests.post(f"{base_url}/api/reset", timeout=5)