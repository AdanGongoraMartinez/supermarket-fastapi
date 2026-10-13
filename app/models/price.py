from sqlmodel import Field

from app.schemas.price import PriceBase


class Price(PriceBase, table=True):
    __tablename__ = "prices"
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", ondelete="CASCADE", index=True)
    supermarket_id: int = Field(
        foreign_key="supermarkets.id", ondelete="CASCADE", index=True
    )
