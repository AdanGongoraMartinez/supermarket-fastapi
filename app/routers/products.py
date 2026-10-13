from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=ProductPublic, status_code=201)
def crear_item(item: ProductCreate, session: SessionDep):
    db_item = Product.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("", response_model=list[ProductPublic])
def listar_products(session: SessionDep):
    return session.exec(select(Product)).all()


@router.get("/{item_id}", response_model=ProductPublic)
def leer_item(item_id: int, session: SessionDep):
    item = session.get(Product, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    return item


@router.patch("/{item_id}", response_model=ProductPublic)
def actualizar_item(item_id: int, datos: ProductUpdate, session: SessionDep):
    item = session.get(Product, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    item.sqlmodel_update(cambios)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def eliminar_item(item_id: int, session: SessionDep):
    item = session.get(Product, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    session.delete(item)
    session.commit()
