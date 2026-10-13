from app.models.supermarket import Supermarket
from app.models import Product
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.price import Price
from app.schemas.price import (
    PriceCreate,
    PricePublic,
    PriceUpdate,
)

router = APIRouter(
    prefix="/prices",
    tags=["prices"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=PricePublic, status_code=201)
def crear_precio(price: PriceCreate, session: SessionDep):
    if not session.get(Product, price.product_id):
        raise HTTPException(status_code=404, detail="El producto no existe")

    if not session.get(Supermarket, price.supermarket_id):
        raise HTTPException(status_code=404, detail="El supermarket no existe")

    db_price = Price.model_validate(price)
    session.add(db_price)
    session.commit()
    session.refresh(db_price)
    return db_price


@router.get("", response_model=list[PricePublic])
def listar_precios(session: SessionDep):
    return session.exec(select(Price)).all()


@router.get("/{price_id}", response_model=PricePublic)
def leer_precio(price_id: int, session: SessionDep):
    price = session.get(Price, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price no encontrado")

    return price


@router.patch("/{price_id}", response_model=PricePublic)
def actualizar_precio(price_id: int, datos: PriceUpdate, session: SessionDep):
    price = session.get(Price, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price no encontrado")

    if not session.get(Product, price.product_id):
        raise HTTPException(status_code=404, detail="El producto no existe")

    if not session.get(Supermarket, price.supermarket_id):
        raise HTTPException(status_code=404, detail="El supermarket no existe")

    cambios = datos.model_dump(exclude_unset=True)
    price.sqlmodel_update(cambios)

    session.add(price)
    session.commit()
    session.refresh(price)
    return price


@router.delete("/{price_id}", status_code=204)
def eliminar_precio(price_id: int, session: SessionDep):
    price = session.get(Price, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price no encontrado")

    session.delete(price)
    session.commit()
