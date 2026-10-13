from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=ItemPublic, status_code=201)
def crear_item(item: ItemCreate, session: SessionDep):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("", response_model=list[ItemPublic])
def listar_products(session: SessionDep):
    return session.exec(select(Item)).all()


@router.get("/{item_id}", response_model=ItemPublic)
def leer_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    return item


@router.patch("/{item_id}", response_model=ItemPublic)
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


@router.delete("/{item_id}", status_code=204)
def eliminar_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    session.delete(item)
    session.commit()
