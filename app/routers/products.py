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
def crear_producto(product: ProductCreate, session: SessionDep):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("", response_model=list[ProductPublic])
def listar_productos(session: SessionDep):
    return session.exec(select(Product)).all()


@router.get("/{product_id}", response_model=ProductPublic)
def leer_producto(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    return product


@router.patch("/{product_id}", response_model=ProductPublic)
def actualizar_producto(product_id: int, datos: ProductUpdate, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    product.sqlmodel_update(cambios)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def eliminar_producto(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product no encontrado")

    session.delete(product)
    session.commit()
