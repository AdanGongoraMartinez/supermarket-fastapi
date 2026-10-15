def test_crear_supermarket(client):
    respuesta = client.post("/supermarkets", json={"name": "Super A"})

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, "name": "Super A"}


def test_crear_supermarket_sin_nombre(client):
    assert client.post("/supermarkets", json={}).status_code == 422


def test_listar_supermarkets(client):
    assert client.get("/supermarkets").json() == []

    client.post("/supermarkets", json={"name": "Super A"})
    client.post("/supermarkets", json={"name": "Super B"})

    respuesta = client.get("/supermarkets")
    assert [supermercado["name"] for supermercado in respuesta.json()] == [
        "Super A",
        "Super B",
    ]


def test_leer_supermarket(client, crear_supermarket):
    supermercado = crear_supermarket(name="Super B")

    respuesta = client.get(f"/supermarkets/{supermercado.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Super B"


def test_leer_supermarket_inexistente(client):
    assert client.get("/supermarkets/999").status_code == 404


def test_actualizar_supermarket(client, crear_supermarket):
    supermercado = crear_supermarket(name="Super A")

    respuesta = client.patch(
        f"/supermarkets/{supermercado.id}", json={"name": "Super A Express"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Super A Express"


def test_actualizar_supermarket_inexistente(client):
    assert client.patch("/supermarkets/999", json={"name": "X"}).status_code == 404


def test_eliminar_supermarket(client, crear_supermarket):
    supermercado = crear_supermarket()

    assert client.delete(f"/supermarkets/{supermercado.id}").status_code == 204
    assert client.get(f"/supermarkets/{supermercado.id}").status_code == 404


def test_eliminar_supermarket_inexistente(client):
    assert client.delete("/supermarkets/999").status_code == 404
