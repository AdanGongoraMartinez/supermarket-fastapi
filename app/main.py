from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import comparer, items, prices, products, supermarkets


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(products.router)
app.include_router(items.router)
app.include_router(supermarkets.router)
app.include_router(prices.router)
app.include_router(comparer.router)
