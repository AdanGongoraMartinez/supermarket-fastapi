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
def crear_supermarket(supermarket: SupermarketCreate, session: SessionDep):
    db_supermarket = Supermarket.model_validate(supermarket)
    session.add(db_supermarket)
    session.commit()
    session.refresh(db_supermarket)
    return db_supermarket


@router.get("", response_model=list[SupermarketPublic])
def listar_supermarkets(session: SessionDep):
    return session.exec(select(Supermarket)).all()


@router.get("/{supermarket_id}", response_model=SupermarketPublic)
def leer_supermarket(supermarket_id: int, session: SessionDep):
    supermarket = session.get(Supermarket, supermarket_id)
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    return supermarket


@router.patch("/{supermarket_id}", response_model=SupermarketPublic)
def actualizar_supermarket(
    supermarket_id: int, datos: SupermarketUpdate, session: SessionDep
):
    supermarket = session.get(Supermarket, supermarket_id)
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    supermarket.sqlmodel_update(cambios)

    session.add(supermarket)
    session.commit()
    session.refresh(supermarket)
    return supermarket


@router.delete("/{supermarket_id}", status_code=204)
def eliminar_supermarket(supermarket_id: int, session: SessionDep):
    supermarket = session.get(Supermarket, supermarket_id)
    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket no encontrado")

    session.delete(supermarket)
    session.commit()
