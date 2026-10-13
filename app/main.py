from contextlib import asynccontextmanager
from typing import Annotated

from db import get_session, init_db
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, select


class ItemBase(SQLModel):
    nombre: str
    precio: float = Field(gt=0)


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemPublic(ItemBase):
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def raiz():
    return {"mensaje": "Hola, FastAPI"}


@app.post("/items", response_model=ItemPublic, status_code=201)
def crear_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.get("/items", response_model=list[ItemPublic])
def listar_items(session: SessionDep):
    return session.exec(select(Item)).all()


@app.get("/items/{item_id}", response_model=ItemPublic)
def leer_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    return item


@app.patch("/items/{item_id}", response_model=ItemPublic)
def actualizar_item(item_id: int, datos: ItemUpdate, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    item.sqlmodel_update(cambios)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=204)
def eliminar_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    session.delete(item)
    session.commit()
