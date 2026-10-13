from sqlmodel import Field

from app.schemas.supermarket import SupermarketBase


class Supermarket(SupermarketBase, table=True):
    __tablename__ = "supermarkets"
    id: int | None = Field(default=None, primary_key=True)
