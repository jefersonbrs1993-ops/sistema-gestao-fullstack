from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_ler_home():
    response = client.get("/")
    assert response.status_code == 200

def test_listar_itens():
    response = client.get("/api/itens")
    assert response.status_code == 200
    assert "dados" in response.json()

def test_criar_item_invalido():
    # Testa a blindagem do Pydantic (quantidade negativa deve retornar erro 422)
    response = client.post("/api/itens", json={"nome": "Teclado", "quantidade": -5})
    assert response.status_code == 422