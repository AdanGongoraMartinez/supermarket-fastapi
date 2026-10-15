PAYLOAD = {
    "name": "Leche",
    "brand": "La Serenísima",
    "presentation": "1L",
    "barcode": None,
}


def test_crear_producto(client):
    respuesta = client.post("/products", json=PAYLOAD)

    assert respuesta.status_code == 201
    body = respuesta.json()
    assert body["id"] == 1
    assert body["name"] == "Leche"
    assert body["brand"] == "La Serenísima"
    assert body["presentation"] == "1L"
    assert body["barcode"] is None


def test_crear_producto_sin_campos_requeridos(client):
    respuesta = client.post("/products", json={"name": "Leche"})

    assert respuesta.status_code == 422


def test_crear_producto_con_barcode(client):
    respuesta = client.post("/products", json={**PAYLOAD, "barcode": "7791234567890"})

    assert respuesta.status_code == 201
    assert respuesta.json()["barcode"] == "7791234567890"


def test_listar_productos(client):
    assert client.get("/products").json() == []

    client.post("/products", json=PAYLOAD)
    client.post("/products", json={**PAYLOAD, "name": "Yerba"})

    respuesta = client.get("/products")
    assert respuesta.status_code == 200
    assert [producto["name"] for producto in respuesta.json()] == ["Leche", "Yerba"]


def test_leer_producto(client, crear_producto):
    producto = crear_producto(name="Yerba")

    respuesta = client.get(f"/products/{producto.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Yerba"


def test_leer_producto_inexistente(client):
    respuesta = client.get("/products/999")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Product no encontrado"


def test_actualizar_producto(client, crear_producto):
    producto = crear_producto(name="Yerba")

    respuesta = client.patch(
        f"/products/{producto.id}", json={**PAYLOAD, "name": "Yerba Mate"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Yerba Mate"
    assert respuesta.json()["id"] == producto.id


def test_actualizar_producto_inexistente(client):
    respuesta = client.patch("/products/999", json=PAYLOAD)

    assert respuesta.status_code == 404


def test_eliminar_producto(client, crear_producto):
    producto = crear_producto()

    respuesta = client.delete(f"/products/{producto.id}")

    assert respuesta.status_code == 204
    assert client.get(f"/products/{producto.id}").status_code == 404
    assert client.get("/products").json() == []


def test_eliminar_producto_inexistente(client):
    assert client.delete("/products/999").status_code == 404
