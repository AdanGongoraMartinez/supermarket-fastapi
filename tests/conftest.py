"""Fixtures y configuración compartida de los tests.

La app usa una base de datos **exclusiva para tests** (`supermarket_test`) que
vive en la misma instancia de Postgres del `docker-compose.yml`.

Detalle clave: `app/db.py` crea el engine a nivel módulo leyendo `DATABASE_URL`,
así que la apuntamos a la base de test **antes** de importar nada de `app`.
`load_dotenv()` no pisa variables ya definidas, por lo que el `.env` de
desarrollo no puede reescribir nuestra URL de test.
"""

import os
from urllib.parse import urlsplit, urlunsplit

import pytest
from dotenv import load_dotenv

load_dotenv()

TEST_DB_NAME = "supermarket_test"


def _misma_url_otra_base(url: str, nombre_base: str) -> str:
    """Devuelve `url` apuntando a otra base de datos del mismo servidor."""
    partes = urlsplit(url)
    return urlunsplit(partes._replace(path=f"/{nombre_base}"))


DEV_DATABASE_URL = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = _misma_url_otra_base(DEV_DATABASE_URL, TEST_DB_NAME)

# Guardia: si esto no termina en "_test" abortamos, para no dropear tablas de dev.
assert urlsplit(TEST_DATABASE_URL).path.strip("/").endswith("test"), (
    f"La base de test debe llamarse *_test, pero es {TEST_DATABASE_URL!r}"
)

# Se setean ANTES de importar `app.*` (ver docstring).
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SQL_ECHO"] = "false"

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.price import Price  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.supermarket import Supermarket  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def crear_base_de_test():
    """Crea `supermarket_test` si no existe y libera el engine al terminar.

    `CREATE DATABASE` no puede correr dentro de una transacción, por eso la
    conexión de administración se abre con autocommit sobre la base `postgres`.
    """
    url_servidor = _misma_url_otra_base(DEV_DATABASE_URL, "postgres")
    engine_servidor = create_engine(url_servidor, isolation_level="AUTOCOMMIT")

    with engine_servidor.connect() as conexion:
        existe = conexion.exec_driver_sql(
            "SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,)
        ).scalar()
        if not existe:
            conexion.exec_driver_sql(f'CREATE DATABASE "{TEST_DB_NAME}"')

    engine_servidor.dispose()
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def base_limpia():
    """Recrea el esquema antes de cada test: aislamiento total, sin residuos.

    No usamos el patrón de rollback con savepoint porque los endpoints hacen
    `commit()` explícito y ese commit sobrevive al rollback del test.
    """
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture
def session():
    """Sesión directa a la base de test, para armar datos sin pasar por HTTP."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    """Cliente HTTP contra la app real, con lifespan (crea tablas si faltan)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def crear_producto(session):
    def _crear_producto(
        name: str = "Leche",
        brand: str | None = "La Serenísima",
        presentation: str = "1L",
        barcode: str | None = None,
    ) -> Product:
        producto = Product(
            name=name, brand=brand, presentation=presentation, barcode=barcode
        )
        session.add(producto)
        session.commit()
        session.refresh(producto)
        return producto

    return _crear_producto


@pytest.fixture
def crear_supermarket(session):
    def _crear_supermarket(name: str = "Super A") -> Supermarket:
        supermercado = Supermarket(name=name)
        session.add(supermercado)
        session.commit()
        session.refresh(supermercado)
        return supermercado

    return _crear_supermarket


@pytest.fixture
def crear_precio(session):
    def _crear_precio(
        producto: Product,
        supermercado: Supermarket,
        price: float = 100.0,
    ) -> Price:
        precio = Price(
            price=price,
            product_id=producto.id,
            supermarket_id=supermercado.id,
        )
        session.add(precio)
        session.commit()
        session.refresh(precio)
        return precio

    return _crear_precio
