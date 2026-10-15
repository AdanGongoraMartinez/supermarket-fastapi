# supermarket-fastapi

API para comparar precios de productos entre supermercados. Proyecto de
**práctica y aprendizaje de [FastAPI](https://fastapi.tiangolo.com/)** usando
SQLModel como ORM y PostgreSQL como base de datos.

El núcleo del dominio son tres entidades: **productos**, **supermercados** y los
**precios** de cada producto en cada supermercado. Con eso se puede calcular la
canasta más barata para una lista de productos.

## Requisitos

- [uv](https://docs.astral.sh/uv/) — gestor de dependencias y entornos (Python 3.12)
- [Docker](https://www.docker.com/) + Docker Compose — para levantar PostgreSQL

## Stack

| Capa              | Tecnología                    |
| ----------------- | ----------------------------- |
| Framework web     | FastAPI (`fastapi[standard]`) |
| ORM / validación  | SQLModel + Pydantic           |
| Base de datos     | PostgreSQL 17                 |
| Driver            | `psycopg` (binary)            |
| Config            | `python-dotenv`               |
| Tests             | `pytest` + `TestClient`       |
| Gestor de entorno | uv                            |

## Estructura del proyecto

```
.
├── app/
│   ├── main.py            # crea la FastAPI app, lifespan y registra los routers
│   ├── db.py              # engine, init_db() y dependencia get_session()
│   ├── models/            # tablas SQLModel (heredan de los schemas *Base)
│   │   ├── product.py
│   │   ├── supermarket.py
│   │   ├── price.py
│   │   └── item.py        # endpoint de ejemplo legado
│   ├── schemas/           # modelos Pydantic/SQLModel: Base / Create / Update / Public
│   │   ├── product.py
│   │   ├── supermarket.py
│   │   ├── price.py
│   │   ├── comparer.py
│   │   └── item.py
│   └── routers/           # endpoints agrupados por recurso
│       ├── products.py
│       ├── supermarkets.py
│       ├── prices.py
│       ├── comparer.py
│       └── items.py
├── tests/                 # suite de pytest (base de datos propia)
│   ├── conftest.py        # fixtures, base de test y factories
│   ├── test_products.py
│   ├── test_supermarkets.py
│   ├── test_prices.py
│   └── test_comparer.py
├── docker-compose.yml     # servicio Postgres
├── pyproject.toml         # metadatos y dependencias
└── .env                   # variables de entorno (no versionado)
```

### Patrón de capas

- **`schemas/`** define los contratos: `*Base` (campos comunes), `*Create`,
  `*Update` y `*Public` (incluye `id`).
- **`models/`** son las tablas reales (`table=True`); heredan de `*Base` y agregan
  la primary key y las foreign keys.
- **`routers/`** implementan el CRUD y dependen de `get_session` para obtener una
  sesión de base de datos por request.

## Puesta en marcha

### 1. Configurar variables de entorno

Creá un archivo `.env` en la raíz (el `.env` real no se versiona):

```env
POSTGRES_USER=app
POSTGRES_PASSWORD=cambia_esto
POSTGRES_DB=mi_api
DATABASE_URL=postgresql+psycopg://app:cambia_esto@localhost:5432/mi_api
```

> `DATABASE_URL` debe coincidir con las credenciales de Postgres. El driver es
> `psycopg` (`postgresql+psycopg://`), no `psycopg2`.

> Opcional: `SQL_ECHO=false` silencia el log de queries SQL del engine. Los tests
> lo usan para no ensuciar la salida.

### 2. Levantar la base de datos

```bash
docker compose up -d
```

El servicio tiene un `healthcheck` con `pg_isready`; podés verificarlo con:

```bash
docker compose ps
```

### 3. Instalar dependencias

```bash
uv sync
```

### 4. Levantar el servidor de desarrollo

```bash
uv run fastapi dev app/main.py
```

Al arrancar, el `lifespan` ejecuta `init_db()`, que crea las tablas que falten
(`SQLModel.metadata.create_all`). **No hay migraciones**: los cambios de esquema
sobre tablas existentes no se aplican automáticamente.

- API: <http://127.0.0.1:8000>
- Swagger UI (docs interactivas): <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Endpoints

Cada recurso (excepto `comparer`) expone el mismo CRUD REST:

| Método   | Ruta             | Descripción                            |
| -------- | ---------------- | -------------------------------------- |
| `POST`   | `/products`      | Crea un producto (201)                 |
| `GET`    | `/products`      | Lista todos los productos              |
| `GET`    | `/products/{id}` | Obtiene un producto (404 si no existe) |
| `PATCH`  | `/products/{id}` | Actualización parcial                  |
| `DELETE` | `/products/{id}` | Elimina (204)                          |

El mismo esquema aplica para `/supermarkets` y `/prices`.

### Comparador de precios

`POST /comparer` — recibe una lista de IDs de productos y devuelve el ranking de
supermercados ordenado por canasta más barata primero (y completo antes que
incompleto).

```json
{ "product_ids": [1, 2, 3] }
```

Respuesta:

```json
{
  "best": {
    "supermarket_id": 1,
    "supermarket_name": "Super A",
    "total": 1150.5,
    "found_products": 3,
    "missing_product_ids": []
  },
  "ranking": [/* ... */]
}
```

Detalles de comportamiento:

- De-duplica los IDs repetidos.
- Si algún producto no existe → `404` con la lista de faltantes.
- Para cada supermercado usa, por producto, el **precio más bajo** disponible.
- Ordena primero los supermercados con la canasta completa y luego por `total`.

### `/items` (ejemplo legado)

`/items` es un CRUD de ejemplo con campos en español (`nombre`, `precio`), usado
para practicar el flujo básico de FastAPI. No forma parte del dominio de
comparación de precios.

## Flujo de prueba rápido

```bash
# 1. Crear un producto
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Leche","brand":"La Serenísima","presentation":"1L","barcode":null}'

# 2. Crear un supermercado
curl -X POST http://127.0.0.1:8000/supermarkets \
  -H "Content-Type: application/json" \
  -d '{"name":"Super A"}'

# 3. Cargar un precio
curl -X POST http://127.0.0.1:8000/prices \
  -H "Content-Type: application/json" \
  -d '{"price":1200.0,"product_id":1,"supermarket_id":1}'

# 4. Comparar
curl -X POST http://127.0.0.1:8000/comparer \
  -H "Content-Type: application/json" \
  -d '{"product_ids":[1]}'
```

## Tests

La suite corre con `pytest` contra una **base de datos exclusiva de test**
(`supermarket_test`), en la misma instancia de Postgres del compose. Tu base de
dev nunca se toca: `tests/conftest.py` deriva la URL de test a partir de
`DATABASE_URL` cambiando solo el nombre de la base, y **aborta si ese nombre no
termina en `test`** (red de seguridad antes de dropear tablas).

```bash
uv run pytest                          # corre la suite
uv run pytest --cov=app                # con cobertura
uv run pytest tests/test_comparer.py   # un solo archivo
```

Cómo funciona:

1. Un fixture de sesión crea `supermarket_test` si no existe (`CREATE DATABASE`).
2. Antes de **cada** test se recrea el esquema (`drop_all` + `create_all`), así
   que cada test arranca con la base vacía. No se usa rollback con savepoint
   porque los endpoints hacen `commit()` explícito y ese commit sobrevive.
3. `client` es el `TestClient` de FastAPI contra la app real (con `lifespan`).
   Los escenarios se arman con las factories `crear_producto`,
   `crear_supermarket` y `crear_precio`.

> El `TestClient` de Starlette 1.8 usa **`httpx2`** (la continuación de HTTPX
> mantenida por Pydantic), no el `httpx` clásico. Por eso está en las
> dependencias de desarrollo; sin él Starlette emite un
> `StarletteDeprecationWarning` y cae al `httpx` viejo.

Los endpoints de `items.py` no tienen tests: es el CRUD de ejemplo legado. En
`prices.py` quedan dos ramas defensivas sin cubrir (la FK garantiza que el
producto y el supermercado existan).

## Notas de desarrollo

- **Actualizaciones parciales**: los `PATCH` usan `model_dump(exclude_unset=True)`
  - `sqlmodel_update`, así que solo se aplican los campos enviados.
- **Validaciones**: `price` debe ser mayor a cero (`Field(gt=0)`); al crear o
  actualizar un precio se valida que existan el producto y el supermercado.
- **Sin migraciones**: por ahora el esquema se gestiona con `create_all`. Si el
  modelo evoluciona, evaluar [Alembic](https://alembic.sqlalchemy.org/).
- **Consultas sin async**: la app usa `Session` sincrónica de SQLModel dentro de
  handlers `def`. Si en algún momento se pasa a `async def`, conviene revisar cómo
  se ejecutan las operaciones bloqueantes de base de datos.

## Roadmap / ideas para practicar

- [x] Tests con `pytest` y `TestClient` (y base de datos de prueba).
- [ ] Tests para el CRUD legado de `/items`.
- [ ] Migraciones con Alembic.
- [ ] Búsqueda/filtrado y paginación en las listas.
- [ ] Categorías de productos (el schema ya menciona `category_id`).
- [ ] Autenticación simple (API key o JWT).
