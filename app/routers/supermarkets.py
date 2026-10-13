from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.supermarket import Supermarket
from app.schemas.supermarket import (
    SupermarketCreate,
    SupermarketPublic,
    SupermarketUpdate,
)

router = APIRouter(
    prefix="/supermarkets",
    tags=["supermarkets"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=SupermarketPublic, status_code=201)
def crear_supermarket(item: SupermarketCreate, session: SessionDep):
    db_item = Supermarket.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("", response_model=list[SupermarketPublic])
def listar_supermarkets(session: SessionDep):
    return session.exec(select(Supermarket)).all()


@router.get("/{item_id}", response_model=SupermarketPublic)
def leer_supermarket(item_id: int, session: SessionDep):
    item = session.get(Supermarket, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    return item


@router.patch("/{item_id}", response_model=SupermarketPublic)
def actualizar_supermarket(item_id: int, datos: SupermarketUpdate, session: SessionDep):
    item = session.get(Supermarket, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    item.sqlmodel_update(cambios)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_supermarket(item_id: int, session: SessionDep):
    item = session.get(Supermarket, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    session.delete(item)
    session.commit()
