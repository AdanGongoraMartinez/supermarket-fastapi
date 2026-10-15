import pytest


def test_crear_precio(client, crear_producto, crear_supermarket):
    producto = crear_producto()
    supermercado = crear_supermarket()

    respuesta = client.post(
        "/prices",
        json={
            "price": 1200.5,
            "product_id": producto.id,
            "supermarket_id": supermercado.id,
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": 1,
        "price": 1200.5,
    }


def test_crear_precio_con_producto_inexistente(client, crear_supermarket):
    supermercado = crear_supermarket()

    respuesta = client.post(
        "/prices",
        json={"price": 100.0, "product_id": 999, "supermarket_id": supermercado.id},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "El producto no existe"


def test_crear_precio_con_supermarket_inexistente(client, crear_producto):
    producto = crear_producto()

    respuesta = client.post(
        "/prices",
        json={"price": 100.0, "product_id": producto.id, "supermarket_id": 999},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "El supermarket no existe"


@pytest.mark.parametrize("precio_invalido", [0, -10.5])
def test_crear_precio_debe_ser_positivo(
    client, crear_producto, crear_supermarket, precio_invalido
):
    producto = crear_producto()
    supermercado = crear_supermarket()

    respuesta = client.post(
        "/prices",
        json={
            "price": precio_invalido,
            "product_id": producto.id,
            "supermarket_id": supermercado.id,
        },
    )

    assert respuesta.status_code == 422


def test_listar_precios(client, crear_producto, crear_supermarket, crear_precio):
    producto = crear_producto()
    supermercado = crear_supermarket()
    crear_precio(producto, supermercado, price=100.0)

    respuesta = client.get("/prices")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 1


def test_leer_precio(client, crear_producto, crear_supermarket, crear_precio):
    precio = crear_precio(crear_producto(), crear_supermarket(), price=250.0)

    respuesta = client.get(f"/prices/{precio.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["price"] == 250.0


def test_leer_precio_inexistente(client):
    respuesta = client.get("/prices/999")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Price no encontrado"


def test_actualizar_precio_inexistente(client, crear_producto, crear_supermarket):
    producto = crear_producto()
    supermercado = crear_supermarket()

    respuesta = client.patch(
        "/prices/999",
        json={
            "price": 99.0,
            "product_id": producto.id,
            "supermarket_id": supermercado.id,
        },
    )

    assert respuesta.status_code == 404


def test_actualizar_precio(client, crear_producto, crear_supermarket, crear_precio):
    producto = crear_producto()
    supermercado = crear_supermarket()
    precio = crear_precio(producto, supermercado, price=100.0)

    respuesta = client.patch(
        f"/prices/{precio.id}",
        json={
            "price": 99.0,
            "product_id": producto.id,
            "supermarket_id": supermercado.id,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["price"] == 99.0


def test_eliminar_precio(client, crear_producto, crear_supermarket, crear_precio):
    precio = crear_precio(crear_producto(), crear_supermarket())

    assert client.delete(f"/prices/{precio.id}").status_code == 204
    assert client.get(f"/prices/{precio.id}").status_code == 404


def test_eliminar_precio_inexistente(client):
    assert client.delete("/prices/999").status_code == 404


def test_eliminar_producto_borra_sus_precios(
    client, crear_producto, crear_supermarket, crear_precio
):
    producto = crear_producto()
    crear_precio(producto, crear_supermarket())

    client.delete(f"/products/{producto.id}")

    assert client.get("/prices").json() == []
