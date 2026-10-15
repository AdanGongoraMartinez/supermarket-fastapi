from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models.price import Price
from app.models.product import Product
from app.models.supermarket import Supermarket
from app.schemas.comparer import (
    ComparerRequest,
    ComparerResult,
    SupermarketComparison,
)

router = APIRouter(
    prefix="/comparer",
    tags=["comparer"],
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=ComparerResult)
def comparar_precios(request: ComparerRequest, session: SessionDep):
    # set() ademas de-duplica la lista de ids
    product_ids = set(request.product_ids)

    existentes = set(
        session.exec(select(Product.id).where(Product.id.in_(list(product_ids)))).all()
    )
    faltantes = product_ids - existentes
    if faltantes:
        raise HTTPException(
            status_code=404,
            detail=f"Productos no encontrados: {sorted(faltantes)}",
        )

    precios = session.exec(
        select(Price).where(Price.product_id.in_(list(product_ids)))
    ).all()

    # supermarket_id -> {product_id: mejor precio}
    canastas: dict[int, dict[int, float]] = defaultdict(dict)
    for precio in precios:
        actual = canastas[precio.supermarket_id].get(precio.product_id)
        if actual is None or precio.price < actual:
            canastas[precio.supermarket_id][precio.product_id] = precio.price

    supermercados = {
        supermarket.id: supermarket
        for supermarket in session.exec(
            select(Supermarket).where(Supermarket.id.in_(list(canastas.keys())))
        ).all()
    }

    ranking = [
        SupermarketComparison(
            supermarket_id=supermarket_id,
            supermarket_name=supermercados[supermarket_id].name,
            total=round(sum(productos.values()), 2),
            found_products=len(productos),
            missing_product_ids=sorted(product_ids - set(productos)),
        )
        for supermarket_id, productos in canastas.items()
    ]

    # Primero las canastas completas (sin faltantes), despues las mas baratas
    ranking.sort(key=lambda c: (len(c.missing_product_ids), c.total))

    return ComparerResult(
        best=ranking[0] if ranking else None,
        ranking=ranking,
    )
