from sqlmodel import Field

from app.schemas.product import ProductBase


class Product(ProductBase, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
