def test_comparer_sin_precios_devuelve_ranking_vacio(client, crear_producto):
    producto = crear_producto()

    respuesta = client.post("/comparer", json={"product_ids": [producto.id]})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"best": None, "ranking": []}


def test_comparer_con_producto_inexistente(client):
    respuesta = client.post("/comparer", json={"product_ids": [1, 2]})

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Productos no encontrados: [1, 2]"


def test_comparer_con_lista_vacia(client):
    respuesta = client.post("/comparer", json={"product_ids": []})

    assert respuesta.status_code == 422


def test_comparer_deduplica_ids_repetidos(
    client, crear_producto, crear_supermarket, crear_precio
):
    producto = crear_producto(name="Leche")
    supermercado = crear_supermarket(name="Super A")
    crear_precio(producto, supermercado, price=100.0)

    respuesta = client.post(
        "/comparer", json={"product_ids": [producto.id, producto.id, producto.id]}
    )

    ranking = respuesta.json()["ranking"]
    assert len(ranking) == 1
    assert ranking[0]["found_products"] == 1
    assert ranking[0]["total"] == 100.0
    assert ranking[0]["missing_product_ids"] == []


def test_comparer_usa_el_precio_mas_bajo_por_supermercado(
    client, crear_producto, crear_supermarket, crear_precio
):
    producto = crear_producto(name="Leche")
    supermercado = crear_supermarket(name="Super A")
    crear_precio(producto, supermercado, price=150.0)
    crear_precio(producto, supermercado, price=100.0)

    respuesta = client.post("/comparer", json={"product_ids": [producto.id]})

    ranking = respuesta.json()["ranking"]
    assert len(ranking) == 1
    assert ranking[0]["total"] == 100.0


def test_comparer_reporta_productos_faltantes(
    client, crear_producto, crear_supermarket, crear_precio
):
    leche = crear_producto(name="Leche")
    yerba = crear_producto(name="Yerba")
    supermercado = crear_supermarket(name="Super A")
    crear_precio(leche, supermercado, price=100.0)

    respuesta = client.post("/comparer", json={"product_ids": [leche.id, yerba.id]})

    ranking = respuesta.json()["ranking"]
    assert len(ranking) == 1
    assert ranking[0]["found_products"] == 1
    assert ranking[0]["missing_product_ids"] == [yerba.id]
    assert ranking[0]["total"] == 100.0


def test_comparer_prioriza_canasta_completa_antes_que_barata(
    client, crear_producto, crear_supermarket, crear_precio
):
    leche = crear_producto(name="Leche")
    yerba = crear_producto(name="Yerba")
    completo = crear_supermarket(name="Completo")
    barato = crear_supermarket(name="Barato")

    # El "Barato" es mucho más económico pero le falta la yerba.
    crear_precio(leche, barato, price=1.0)
    crear_precio(leche, completo, price=100.0)
    crear_precio(yerba, completo, price=100.0)

    respuesta = client.post("/comparer", json={"product_ids": [leche.id, yerba.id]})

    ranking = respuesta.json()["ranking"]
    assert [canasta["supermarket_name"] for canasta in ranking] == [
        "Completo",
        "Barato",
    ]
    assert respuesta.json()["best"]["supermarket_name"] == "Completo"


def test_comparer_ordena_por_total_entre_canastas_completas(
    client, crear_producto, crear_supermarket, crear_precio
):
    leche = crear_producto(name="Leche")
    yerba = crear_producto(name="Yerba")
    caro = crear_supermarket(name="Caro")
    barato = crear_supermarket(name="Barato")

    crear_precio(leche, caro, price=100.0)
    crear_precio(yerba, caro, price=100.0)
    crear_precio(leche, barato, price=50.0)
    crear_precio(yerba, barato, price=50.0)

    respuesta = client.post("/comparer", json={"product_ids": [leche.id, yerba.id]})

    ranking = respuesta.json()["ranking"]
    assert [canasta["supermarket_name"] for canasta in ranking] == [
        "Barato",
        "Caro",
    ]
    assert [canasta["total"] for canasta in ranking] == [100.0, 200.0]
    assert respuesta.json()["best"] == ranking[0]
